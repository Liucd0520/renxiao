import json 
from decimal import Decimal

class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)  # 或 str(obj)，根据需求选择
        return super().default(obj)