#!/usr/bin/env python3
"""
SQL Researcher Web UI - 一个简单易用的前端界面
启动命令: python web_ui.py
"""

import asyncio
import json
import os
import re
import time
from datetime import datetime
from pathlib import Path

import httpx
from flask import Flask, render_template_string, request, jsonify, send_file
import markdown

app = Flask(__name__)

API_BASE = 'http://127.0.0.1:2024'
REPORTS_DIR = Path(__file__).parent / 'reports'
REPORTS_DIR.mkdir(exist_ok=True)

# 存储运行状态
runs = {}

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SQL Researcher - 智能数据分析助手</title>
    <link href="https://cdn.jsdelivr.net/npm/github-markdown-css@5.2.0/github-markdown-dark.min.css" rel="stylesheet">
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'PingFang SC', sans-serif;
            background: linear-gradient(135deg, #0f0f23 0%, #1a1a3e 50%, #0f0f23 100%);
            min-height: 100vh;
            color: #e0e0e0;
        }
        .header {
            background: rgba(0,0,0,0.3);
            padding: 20px;
            text-align: center;
            border-bottom: 1px solid rgba(0,212,255,0.3);
        }
        .header h1 {
            font-size: 28px;
            background: linear-gradient(90deg, #00d4ff, #7b2ff7, #00d4ff);
            background-size: 200% auto;
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            animation: gradient 3s ease infinite;
        }
        @keyframes gradient {
            0% { background-position: 0% center; }
            50% { background-position: 100% center; }
            100% { background-position: 0% center; }
        }
        .container { max-width: 1000px; margin: 0 auto; padding: 20px; }
        
        /* 状态卡片 */
        .status-bar {
            display: flex;
            align-items: center;
            gap: 15px;
            padding: 15px 20px;
            background: rgba(0,0,0,0.4);
            border-radius: 12px;
            margin-bottom: 20px;
        }
        .status-dot {
            width: 12px; height: 12px;
            border-radius: 50%;
            background: #ff4444;
            box-shadow: 0 0 10px #ff4444;
        }
        .status-dot.connected {
            background: #44ff44;
            box-shadow: 0 0 10px #44ff44;
        }
        
        /* 卡片样式 */
        .card {
            background: rgba(30,30,60,0.8);
            border-radius: 16px;
            padding: 25px;
            margin-bottom: 20px;
            border: 1px solid rgba(0,212,255,0.2);
            backdrop-filter: blur(10px);
        }
        .card h3 {
            color: #00d4ff;
            margin-bottom: 15px;
            font-size: 18px;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        /* 输入区域 */
        textarea {
            width: 100%;
            min-height: 120px;
            padding: 15px;
            border: 2px solid rgba(0,212,255,0.3);
            border-radius: 12px;
            background: rgba(0,0,0,0.4);
            color: #fff;
            font-size: 15px;
            resize: vertical;
            transition: border-color 0.3s;
        }
        textarea:focus {
            outline: none;
            border-color: #00d4ff;
        }
        
        /* 按钮 */
        .btn {
            background: linear-gradient(135deg, #00d4ff 0%, #7b2ff7 100%);
            color: #fff;
            border: none;
            padding: 14px 32px;
            border-radius: 10px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            margin-top: 15px;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(0,212,255,0.4);
        }
        .btn:disabled {
            background: #444;
            cursor: not-allowed;
            transform: none;
            box-shadow: none;
        }
        .btn-secondary {
            background: rgba(0,212,255,0.2);
            border: 1px solid #00d4ff;
        }
        
        /* 进度条 */
        .progress-container {
            margin: 20px 0;
        }
        .progress-bar {
            height: 8px;
            background: rgba(0,0,0,0.4);
            border-radius: 4px;
            overflow: hidden;
        }
        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #00d4ff, #7b2ff7);
            border-radius: 4px;
            transition: width 0.5s ease;
            position: relative;
        }
        .progress-fill::after {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent);
            animation: shimmer 1.5s infinite;
        }
        @keyframes shimmer {
            0% { transform: translateX(-100%); }
            100% { transform: translateX(100%); }
        }
        .progress-text {
            display: flex;
            justify-content: space-between;
            margin-top: 8px;
            font-size: 14px;
            color: #aaa;
        }
        
        /* 步骤指示器 */
        .steps {
            display: flex;
            justify-content: space-between;
            margin: 25px 0;
            position: relative;
        }
        .steps::before {
            content: '';
            position: absolute;
            top: 20px;
            left: 10%;
            right: 10%;
            height: 2px;
            background: rgba(255,255,255,0.2);
        }
        .step {
            text-align: center;
            z-index: 1;
        }
        .step-circle {
            width: 40px;
            height: 40px;
            border-radius: 50%;
            background: rgba(0,0,0,0.6);
            border: 2px solid #444;
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0 auto 8px;
            font-size: 18px;
            transition: all 0.3s;
        }
        .step.active .step-circle {
            border-color: #00d4ff;
            box-shadow: 0 0 15px rgba(0,212,255,0.5);
        }
        .step.completed .step-circle {
            background: #00d4ff;
            border-color: #00d4ff;
        }
        .step-label {
            font-size: 12px;
            color: #888;
        }
        .step.active .step-label,
        .step.completed .step-label {
            color: #00d4ff;
        }
        
        /* 审核区域 */
        .review-box {
            background: rgba(255,153,0,0.1);
            border: 2px solid #ff9900;
            border-radius: 12px;
            padding: 20px;
            margin: 20px 0;
        }
        .review-box h4 {
            color: #ff9900;
            margin-bottom: 15px;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        .review-content {
            background: rgba(0,0,0,0.3);
            border-radius: 8px;
            padding: 15px;
            white-space: pre-wrap;
            font-family: 'Monaco', 'Menlo', monospace;
            font-size: 14px;
            max-height: 300px;
            overflow-y: auto;
        }
        .review-actions {
            display: flex;
            gap: 10px;
            margin-top: 15px;
        }
        .review-actions input {
            flex: 1;
            padding: 12px;
            border: 1px solid #444;
            border-radius: 8px;
            background: rgba(0,0,0,0.4);
            color: #fff;
            font-size: 14px;
        }
        
        /* 报告区域 */
        .report-container {
            background: rgba(0,0,0,0.4);
            border-radius: 12px;
            padding: 25px;
            margin-top: 20px;
        }
        .report-actions {
            display: flex;
            gap: 10px;
            margin-bottom: 15px;
        }
        .markdown-body {
            background: transparent !important;
            color: #e0e0e0 !important;
        }
        .markdown-body pre {
            background: rgba(0,0,0,0.4) !important;
        }
        .markdown-body table {
            display: block;
            overflow-x: auto;
        }
        
        /* 日志 */
        .log-container {
            background: rgba(0,0,0,0.4);
            border-radius: 8px;
            padding: 15px;
            font-family: 'Monaco', 'Menlo', monospace;
            font-size: 13px;
            max-height: 200px;
            overflow-y: auto;
        }
        .log-entry { margin: 4px 0; }
        .log-time { color: #666; }
        .log-success { color: #44ff44; }
        .log-error { color: #ff4444; }
        .log-info { color: #00d4ff; }
        .log-warning { color: #ff9900; }
        
        .hidden { display: none !important; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🔬 SQL Researcher - 智能数据分析助手</h1>
    </div>
    
    <div class="container">
        <!-- 状态栏 -->
        <div class="status-bar">
            <div class="status-dot" id="statusDot"></div>
            <span id="statusText">检查服务器连接...</span>
        </div>
        
        <!-- 步骤指示器 -->
        <div class="steps" id="stepsContainer">
            <div class="step" data-step="1">
                <div class="step-circle">📝</div>
                <div class="step-label">输入问题</div>
            </div>
            <div class="step" data-step="2">
                <div class="step-circle">🔍</div>
                <div class="step-label">问题拆解</div>
            </div>
            <div class="step" data-step="3">
                <div class="step-circle">✅</div>
                <div class="step-label">人工审核</div>
            </div>
            <div class="step" data-step="4">
                <div class="step-circle">⚙️</div>
                <div class="step-label">SQL执行</div>
            </div>
            <div class="step" data-step="5">
                <div class="step-circle">📊</div>
                <div class="step-label">生成报告</div>
            </div>
        </div>
        
        <!-- 输入区域 -->
        <div class="card" id="inputCard">
            <h3>📝 输入您的问题</h3>
            <textarea id="question" placeholder="例如：我想了解一下咱们平台的整体情况。客户数量和设备数量大概是多少？上个月设备的上下线情况怎么样？"></textarea>
            <button class="btn" id="submitBtn" onclick="submitQuestion()">🚀 开始分析</button>
        </div>
        
        <!-- 进度区域 -->
        <div class="card hidden" id="progressCard">
            <h3>⏳ 正在处理</h3>
            <div class="progress-container">
                <div class="progress-bar">
                    <div class="progress-fill" id="progressFill" style="width: 0%"></div>
                </div>
                <div class="progress-text">
                    <span id="progressStatus">准备中...</span>
                    <span id="progressPercent">0%</span>
                </div>
            </div>
        </div>
        
        <!-- 审核区域 -->
        <div class="card hidden" id="reviewCard">
            <h3>⏸️ 需要您的确认</h3>
            <div class="review-box">
                <h4>🔍 问题拆解结果</h4>
                <div class="review-content" id="reviewContent"></div>
                <div class="review-actions">
                    <input type="text" id="feedbackInput" placeholder="输入 yes 确认执行，或输入修改建议...">
                    <button class="btn" onclick="sendFeedback()">发送</button>
                </div>
            </div>
        </div>
        
        <!-- 报告区域 -->
        <div class="card hidden" id="reportCard">
            <h3>📊 分析报告</h3>
            <div class="report-actions">
                <button class="btn btn-secondary" onclick="downloadReport()">📥 下载报告</button>
                <button class="btn btn-secondary" onclick="newAnalysis()">🔄 新建分析</button>
            </div>
            <div class="report-container">
                <div class="markdown-body" id="reportContent"></div>
            </div>
        </div>
        
        <!-- 日志区域 -->
        <div class="card">
            <h3>📋 执行日志</h3>
            <div class="log-container" id="logContainer"></div>
        </div>
    </div>

    <script>
        let threadId = null;
        let assistantId = null;
        let currentRunId = null;
        let currentReport = '';
        let pollInterval = null;
        
        function log(msg, type = '') {
            const container = document.getElementById('logContainer');
            const time = new Date().toLocaleTimeString();
            container.innerHTML += `<div class="log-entry"><span class="log-time">[${time}]</span> <span class="log-${type}">${msg}</span></div>`;
            container.scrollTop = container.scrollHeight;
        }
        
        function setStep(stepNum) {
            document.querySelectorAll('.step').forEach((el, i) => {
                el.classList.remove('active', 'completed');
                if (i + 1 < stepNum) el.classList.add('completed');
                else if (i + 1 === stepNum) el.classList.add('active');
            });
        }
        
        function setProgress(percent, status) {
            document.getElementById('progressFill').style.width = percent + '%';
            document.getElementById('progressPercent').textContent = percent + '%';
            document.getElementById('progressStatus').textContent = status;
        }
        
        async function checkConnection() {
            try {
                const res = await fetch('/api/status');
                const data = await res.json();
                if (data.connected) {
                    assistantId = data.assistant_id;
                    document.getElementById('statusDot').classList.add('connected');
                    document.getElementById('statusText').textContent = '已连接到 SQL Researcher';
                    log('服务器连接成功', 'success');
                    setStep(1);
                } else {
                    throw new Error(data.error || '连接失败');
                }
            } catch (e) {
                document.getElementById('statusText').textContent = '服务器未启动 - 请先运行 langgraph dev';
                log('连接失败: ' + e.message, 'error');
            }
        }
        
        async function submitQuestion() {
            const question = document.getElementById('question').value.trim();
            if (!question) return alert('请输入问题');
            
            document.getElementById('submitBtn').disabled = true;
            document.getElementById('progressCard').classList.remove('hidden');
            document.getElementById('reviewCard').classList.add('hidden');
            document.getElementById('reportCard').classList.add('hidden');
            
            setStep(2);
            setProgress(10, '创建分析任务...');
            
            try {
                log('提交问题: ' + question.substring(0, 50) + '...', 'info');
                
                const res = await fetch('/api/submit', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ question })
                });
                const data = await res.json();
                
                if (data.error) throw new Error(data.error);
                
                threadId = data.thread_id;
                currentRunId = data.run_id;
                log('任务已创建: ' + currentRunId.substring(0, 8) + '...', 'info');
                
                setProgress(20, '正在分析问题...');
                startPolling();
                
            } catch (e) {
                log('错误: ' + e.message, 'error');
                document.getElementById('submitBtn').disabled = false;
            }
        }
        
        function startPolling() {
            if (pollInterval) clearInterval(pollInterval);
            pollInterval = setInterval(pollStatus, 2000);
        }
        
        // 记录上一次的进度，用于检测变化
        let lastProgress = {sql_results_count: 0, notes_count: 0, stage: ''};
        
        async function pollStatus() {
            try {
                const res = await fetch(`/api/status/${threadId}/${currentRunId}`);
                const data = await res.json();
                
                if (data.interrupted) {
                    clearInterval(pollInterval);
                    setStep(3);
                    setProgress(50, '等待人工审核...');
                    document.getElementById('reviewContent').textContent = data.interrupt_message;
                    document.getElementById('reviewCard').classList.remove('hidden');
                    if (data.sub_questions_count) {
                        log(`问题已拆解为 ${data.sub_questions_count} 个子问题`, 'info');
                    }
                    log('需要确认问题拆解', 'warning');
                    return;
                }
                
                if (data.status === 'success') {
                    clearInterval(pollInterval);
                    setStep(5);
                    setProgress(100, '分析完成！');
                    showReport(data.report);
                    document.getElementById('submitBtn').disabled = false;
                    log('分析完成！', 'success');
                    return;
                }
                
                if (data.status === 'error') {
                    clearInterval(pollInterval);
                    log('执行错误', 'error');
                    document.getElementById('submitBtn').disabled = false;
                    return;
                }
                
                // 检测并记录进度变化
                if (data.sql_results_count > lastProgress.sql_results_count) {
                    log(`✅ SQL 查询完成: ${data.sql_results_count}/${data.sub_questions_count || '?'}`, 'success');
                    lastProgress.sql_results_count = data.sql_results_count;
                }
                if (data.notes_count > lastProgress.notes_count) {
                    log(`📝 研究笔记: ${data.notes_count}/${data.sub_questions_count || '?'}`, 'info');
                    lastProgress.notes_count = data.notes_count;
                }
                if (data.stage_desc && data.stage_desc !== lastProgress.stage) {
                    log(data.stage_desc, 'info');
                    lastProgress.stage = data.stage_desc;
                }
                
                // 更新进度条
                if (data.current_node) {
                    const nodes = ['decompose_question', 'review_decomposition', 'sql_research_supervisor', 'sql_researcher', 'final_sql_report'];
                    const idx = nodes.indexOf(data.current_node);
                    if (idx >= 0) {
                        const progress = 30 + (idx * 15);
                        const statusText = data.stage_desc || ('正在执行: ' + data.current_node);
                        setProgress(progress, statusText);
                        setStep(Math.min(idx + 2, 5));
                    }
                }
                
            } catch (e) {
                log('状态查询错误: ' + e.message, 'error');
            }
        }
        
        async function sendFeedback() {
            const feedback = document.getElementById('feedbackInput').value.trim();
            if (!feedback) return alert('请输入确认或修改建议');
            
            document.getElementById('reviewCard').classList.add('hidden');
            setStep(4);
            setProgress(60, '正在执行SQL查询...');
            
            try {
                log('发送反馈: ' + feedback, 'info');
                
                const res = await fetch('/api/resume', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ thread_id: threadId, feedback })
                });
                const data = await res.json();
                
                if (data.error) throw new Error(data.error);
                
                currentRunId = data.run_id;
                document.getElementById('feedbackInput').value = '';
                startPolling();
                
            } catch (e) {
                log('发送反馈失败: ' + e.message, 'error');
            }
        }
        
        function showReport(report) {
            currentReport = report || '暂无报告';
            document.getElementById('reportContent').innerHTML = marked.parse(currentReport);
            document.getElementById('reportCard').classList.remove('hidden');
            document.getElementById('progressCard').classList.add('hidden');
        }
        
        async function downloadReport() {
            const blob = new Blob([currentReport], { type: 'text/markdown' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `report_${new Date().toISOString().slice(0,10)}.md`;
            a.click();
            URL.revokeObjectURL(url);
        }
        
        function newAnalysis() {
            document.getElementById('submitBtn').disabled = false;
            document.getElementById('progressCard').classList.add('hidden');
            document.getElementById('reviewCard').classList.add('hidden');
            document.getElementById('reportCard').classList.add('hidden');
            document.getElementById('question').value = '';
            setStep(1);
            setProgress(0, '');
            threadId = null;
            currentRunId = null;
            lastProgress = {sql_results_count: 0, notes_count: 0, stage: ''};  // 重置进度
        }
        
        // Markdown 解析器
        function marked_parse(text) {
            return text
                .replace(/^### (.*$)/gm, '<h3>$1</h3>')
                .replace(/^## (.*$)/gm, '<h2>$1</h2>')
                .replace(/^# (.*$)/gm, '<h1>$1</h1>')
                .replace(/\\*\\*(.*?)\\*\\*/g, '<strong>$1</strong>')
                .replace(/\\*(.*?)\\*/g, '<em>$1</em>')
                .replace(/```(.*?)```/gs, '<pre><code>$1</code></pre>')
                .replace(/`(.*?)`/g, '<code>$1</code>')
                .replace(/\\n/g, '<br>');
        }
        
        // 初始化
        checkConnection();
    </script>
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
</body>
</html>
'''


@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)


@app.route('/api/status')
def api_status():
    try:
        with httpx.Client(timeout=10) as client:
            res = client.post(f'{API_BASE}/assistants/search', json={'limit': 10})
            data = res.json()
            sql_researcher = next((a for a in data if a['name'] == 'SQL Researcher'), None)
            if sql_researcher:
                return jsonify({'connected': True, 'assistant_id': sql_researcher['assistant_id']})
            return jsonify({'connected': False, 'error': 'SQL Researcher not found'})
    except Exception as e:
        return jsonify({'connected': False, 'error': str(e)})


@app.route('/api/submit', methods=['POST'])
def api_submit():
    try:
        data = request.json
        question = data.get('question', '')
        
        with httpx.Client(timeout=30) as client:
            # 获取 assistant
            res = client.post(f'{API_BASE}/assistants/search', json={'limit': 10})
            assistants = res.json()
            assistant_id = next(a['assistant_id'] for a in assistants if a['name'] == 'SQL Researcher')
            
            # 创建 thread
            res = client.post(f'{API_BASE}/threads', json={})
            thread_id = res.json()['thread_id']
            
            # 发送问题
            res = client.post(
                f'{API_BASE}/threads/{thread_id}/runs',
                json={
                    'assistant_id': assistant_id,
                    'input': {'messages': [{'role': 'user', 'content': question}]}
                }
            )
            run_id = res.json()['run_id']
            
            runs[run_id] = {'thread_id': thread_id, 'assistant_id': assistant_id}
            
            return jsonify({'thread_id': thread_id, 'run_id': run_id})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/status/<thread_id>/<run_id>')
def api_run_status(thread_id, run_id):
    try:
        with httpx.Client(timeout=30) as client:
            # 先检查 run 状态
            run_res = client.get(f'{API_BASE}/threads/{thread_id}/runs/{run_id}')
            run = run_res.json()
            run_status = run.get('status', '')
            
            # 如果 run 正在运行，说明已经 resume 了，不再检查旧的 interrupt
            if run_status == 'pending':
                return jsonify({'status': 'running', 'current_node': 'starting'})
            
            # 获取 state
            state_res = client.get(f'{API_BASE}/threads/{thread_id}/state')
            state = state_res.json()
            
            # 提取进度信息
            values = state.get('values', {})
            sub_questions = values.get('sub_questions', [])
            sql_results = values.get('sql_results', [])
            notes = values.get('notes', [])
            
            progress_info = {
                'sub_questions_count': len(sub_questions),
                'sql_results_count': len(sql_results),
                'notes_count': len(notes),
            }
            
            # 只有当 run 结束（success/error/interrupted）时才检查 interrupt
            if run_status in ['success', 'error', 'interrupted']:
                # 检查是否有待处理的 interrupt
                if state.get('tasks'):
                    for task in state['tasks']:
                        if task.get('interrupts'):
                            return jsonify({
                                'status': 'interrupted',
                                'interrupted': True,
                                'interrupt_message': task['interrupts'][0]['value'],
                                **progress_info
                            })
                
                # 没有 interrupt，检查最终结果
                if run_status == 'success':
                    report = values.get('final_report', '')
                    return jsonify({
                        'status': 'success', 
                        'report': report,
                        **progress_info
                    })
                elif run_status == 'error':
                    return jsonify({'status': 'error', **progress_info})
            
            # run 仍在运行中 - 返回当前节点和进度
            current_node = state.get('next', [''])[0] if state.get('next') else run.get('current_node', '')
            
            # 根据当前节点和进度确定阶段描述
            # 如果已经有 sql_results 或 notes，说明已经在执行研究了
            if sql_results or notes:
                stage_desc = f'正在执行 SQL 研究... ({len(sql_results)}/{len(sub_questions)} 完成)'
            elif current_node == 'review_decomposition' and run_status == 'running':
                # resume 后正在执行并行研究
                stage_desc = '正在并行执行 FusionSQL 查询...'
            else:
                stage_desc = {
                    'decompose_question': '正在拆解问题...',
                    'review_decomposition': '等待用户确认...',
                    'sql_research_supervisor': '正在调度研究任务...',
                    '_execute_parallel_research': '正在并行执行 FusionSQL 查询...',
                    'sql_researcher': '正在执行 SQL 研究...',
                    'sql_researcher_tools': '正在执行工具调用...',
                    'compress_sql_research': '正在压缩研究结果...',
                    'final_sql_report': '正在生成最终报告...',
                }.get(current_node, f'正在执行: {current_node}')
            
            return jsonify({
                'status': 'running', 
                'current_node': current_node,
                'stage_desc': stage_desc,
                **progress_info
            })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/resume', methods=['POST'])
def api_resume():
    try:
        data = request.json
        thread_id = data['thread_id']
        feedback = data['feedback']
        
        run_info = next((v for v in runs.values() if v['thread_id'] == thread_id), None)
        if not run_info:
            return jsonify({'error': 'Thread not found'}), 404
        
        with httpx.Client(timeout=30) as client:
            res = client.post(
                f'{API_BASE}/threads/{thread_id}/runs',
                json={
                    'assistant_id': run_info['assistant_id'],
                    'command': {'resume': feedback}
                }
            )
            run_id = res.json()['run_id']
            runs[run_id] = run_info
            
            return jsonify({'run_id': run_id})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    print('''
╔══════════════════════════════════════════════════════════════╗
║                  SQL Researcher Web UI                       ║
╠══════════════════════════════════════════════════════════════╣
║  请先在另一个终端启动 LangGraph 服务器:                         ║
║  cd open_deep_research && langgraph dev --no-browser         ║
╠══════════════════════════════════════════════════════════════╣
║  然后访问: http://127.0.0.1:5001                              ║
╚══════════════════════════════════════════════════════════════╝
''')
    app.run(host='0.0.0.0', port=5001, debug=True)
