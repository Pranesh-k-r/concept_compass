import re

class SafeMathSolver:
    """
    A safe, limited rule-based math solver that does not use eval().
    Supports:
    - Basic arithmetic (e.g. 5 + 3 * 2)
    - One-step linear equations (e.g. x + 5 = 12, 3x = 15)
    """
    
    def solve(self, expression):
        expression = expression.replace(" ", "")
        
        # Check if it's an equation
        if "=" in expression:
            return self._solve_equation(expression)
        else:
            return self._solve_arithmetic(expression)
            
    def _solve_equation(self, expr):
        parts = expr.split("=")
        if len(parts) != 2:
            return {"error": "Only one '=' sign is supported."}
            
        left, right = parts
        
        # Support ax = b
        match_ax = re.match(r"^([+-]?\d*)x$", left)
        if match_ax and right.lstrip("+-").isdigit():
            a_str = match_ax.group(1)
            a = int(a_str) if a_str not in ["", "+", "-"] else (1 if a_str != "-" else -1)
            b = int(right)
            
            steps = [
                f"Equation: {expr}",
                f"Divide both sides by {a} to isolate x.",
                f"x = {b} / {a}",
            ]
            if a == 0:
                return {"error": "Cannot divide by 0."}
                
            steps.append(f"x = {b/a:g}")
            return {"steps": steps}
            
        # Support x + a = b
        match_xa = re.match(r"^x([+-]\d+)$", left)
        if match_xa and right.lstrip("+-").isdigit():
            a = int(match_xa.group(1))
            b = int(right)
            
            op = "Subtract" if a > 0 else "Add"
            abs_a = abs(a)
            
            steps = [
                f"Equation: {expr}",
                f"{op} {abs_a} to both sides to isolate x.",
                f"x = {b} {'-' if a > 0 else '+'} {abs_a}",
                f"x = {b - a}"
            ]
            return {"steps": steps}
            
        return {"error": "Unsupported equation format. Try '3x=15' or 'x+5=12'."}

    def _solve_arithmetic(self, expr):
        # Extremely basic order of operations using regex to avoid eval()
        if not re.match(r"^[0-9+\-*/.]+$", expr):
            return {"error": "Invalid characters in expression. Only numbers and + - * / are allowed."}
            
        steps = [f"Expression: {expr}"]
        current = expr
        
        try:
            # First handle multiplication and division
            while re.search(r"(\d+\.?\d*)([*/])(\d+\.?\d*)", current):
                match = re.search(r"(\d+\.?\d*)([*/])(\d+\.?\d*)", current)
                left = float(match.group(1))
                op = match.group(2)
                right = float(match.group(3))
                
                if op == '*':
                    res = left * right
                else:
                    if right == 0: return {"error": "Division by zero."}
                    res = left / right
                    
                current = current[:match.start()] + str(res) + current[match.end():]
                steps.append(f"Calculate {match.group(0)} = {res:g}")
                steps.append(f"New expression: {current}")
                
            # Then handle addition and subtraction
            while re.search(r"(-?\d+\.?\d*)([+-])(\d+\.?\d*)", current):
                match = re.search(r"(-?\d+\.?\d*)([+-])(\d+\.?\d*)", current)
                
                left = float(match.group(1))
                op = match.group(2)
                right = float(match.group(3))
                
                if op == '+':
                    res = left + right
                else:
                    res = left - right
                    
                current = current[:match.start()] + str(res) + current[match.end():]
                steps.append(f"Calculate {match.group(0)} = {res:g}")
                steps.append(f"New expression: {current}")

            # Return final
            return {"steps": steps}
        except Exception as e:
            return {"error": "Could not parse expression."}
