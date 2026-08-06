"""
IITIAN AI - Intelligent Calculator & Unit Converter Tool
Handles mathematical evaluation, unit conversions, percentages, and student calculations safely.
"""

import math
import re

def calculate(expression: str) -> dict:
    """
    Evaluates mathematical expressions and unit conversions safely.
    """
    expr = expression.strip().lower()
    
    # Check for Unit Conversions
    conv_result = _handle_conversion(expr)
    if conv_result:
        return conv_result

    # Check for CGPA to percentage
    cgpa_match = re.search(r'(?:cgpa|gpa)\s*([0-9.]+)', expr)
    if cgpa_match:
        val = float(cgpa_match.group(1))
        pct = round(val * 9.5, 2)
        return {
            "success": True,
            "expression": expression,
            "result": f"{pct}%",
            "message": f"A CGPA of {val} is approximately {pct}% (using CBSE/IIT standard formula: CGPA × 9.5)."
        }

    # Check for "X% of Y"
    pct_match = re.search(r'([0-9.]+)\s*%\s*(?:of)?\s*([0-9.]+)', expr)
    if pct_match:
        p = float(pct_match.group(1))
        total = float(pct_match.group(2))
        res = round((p / 100.0) * total, 4)
        return {
            "success": True,
            "expression": expression,
            "result": str(res),
            "message": f"{p}% of {total} is {res}."
        }

    # Clean expression for safe math eval
    clean_expr = expr.replace("×", "*").replace("÷", "/").replace("x", "*").replace("times", "*").replace("multiplied by", "*")
    clean_expr = clean_expr.replace("divided by", "/").replace("plus", "+").replace("minus", "-")
    clean_expr = clean_expr.replace("^", "**")

    # Keep only digits, operators, math functions
    safe_chars = set("0123456789.+-*/() %")
    filtered = "".join([c for c in clean_expr if c in safe_chars])

    try:
        # Restricted safe eval
        allowed_names = {
            "sqrt": math.sqrt,
            "sin": math.sin,
            "cos": math.cos,
            "tan": math.tan,
            "pi": math.pi,
            "e": math.e,
            "pow": pow,
            "abs": abs,
            "round": round
        }
        res = eval(filtered, {"__builtins__": None}, allowed_names)
        res_formatted = int(res) if isinstance(res, float) and res.is_integer() else round(res, 4)
        return {
            "success": True,
            "expression": expression,
            "result": str(res_formatted),
            "message": f"The result of {expression} is {res_formatted}."
        }
    except Exception as e:
        return {
            "success": False,
            "expression": expression,
            "error": str(e),
            "message": f"Could not calculate '{expression}'."
        }

def _handle_conversion(expr: str):
    # km to miles
    m = re.search(r'([0-9.]+)\s*(?:km|kilometers?)\s*(?:to|in|into)\s*(?:miles?)', expr)
    if m:
        km = float(m.group(1))
        miles = round(km * 0.621371, 2)
        return {"success": True, "expression": expr, "result": f"{miles} miles", "message": f"{km} kilometers is {miles} miles."}

    # miles to km
    m = re.search(r'([0-9.]+)\s*(?:miles?)\s*(?:to|in|into)\s*(?:km|kilometers?)', expr)
    if m:
        miles = float(m.group(1))
        km = round(miles * 1.60934, 2)
        return {"success": True, "expression": expr, "result": f"{km} km", "message": f"{miles} miles is {km} kilometers."}

    # celsius to fahrenheit
    m = re.search(r'([0-9.]+)\s*(?:c|celsius)\s*(?:to|in|into)\s*(?:f|fahrenheit)', expr)
    if m:
        c = float(m.group(1))
        f = round((c * 9/5) + 32, 2)
        return {"success": True, "expression": expr, "result": f"{f}°F", "message": f"{c}°C is {f}°F."}

    # kg to pounds
    m = re.search(r'([0-9.]+)\s*(?:kg|kilograms?)\s*(?:to|in|into)\s*(?:lbs?|pounds?)', expr)
    if m:
        kg = float(m.group(1))
        lbs = round(kg * 2.20462, 2)
        return {"success": True, "expression": expr, "result": f"{lbs} lbs", "message": f"{kg} kg is {lbs} pounds."}

    return None
