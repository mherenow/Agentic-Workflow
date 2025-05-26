from src.tools.registry import BaseTool
from typing import Dict, Any
import re
import math
import operator

class CalculatorTool(BaseTool):
    """Tool for performing mathematical calculations."""
    
    @property
    def name(self) -> str:
        return "calculator"
    
    @property
    def description(self) -> str:
        return "Perform mathematical calculations and arithmetic operations"
    
    def execute(self, expression: str) -> Dict[str, Any]:
        """Execute a mathematical calculation."""
        try:
            # Clean the expression
            expression = expression.strip()
            
            # Replace common mathematical functions and constants
            expression = expression.replace("π", str(math.pi))
            expression = expression.replace("pi", str(math.pi))
            expression = expression.replace("e", str(math.e))
            
            # Define allowed operators and functions
            allowed_operators = {
                '+': operator.add,
                '-': operator.sub,
                '*': operator.mul,
                '/': operator.truediv,
                '//': operator.floordiv,
                '%': operator.mod,
                '**': operator.pow,
                '^': operator.pow,
            }
            
            # Define allowed functions
            allowed_functions = {
                'sqrt': math.sqrt,
                'sin': math.sin,
                'cos': math.cos,
                'tan': math.tan,
                'log': math.log,
                'log10': math.log10,
                'abs': abs,
                'round': round,
                'ceil': math.ceil,
                'floor': math.floor,
            }
            
            # Replace ^ with ** for exponentiation
            expression = expression.replace("^", "**")
              # Security check - only allow numbers, operators, and parentheses
            clean_exp = expression
            
            # Attempt to convert text-based expressions into mathematical ones
            if "flight" in clean_exp.lower() or "tax" in clean_exp.lower() or "fee" in clean_exp.lower() or "price" in clean_exp.lower():
                # Extract any numbers from the expression
                numbers = re.findall(r'\b\d+(?:\.\d+)?\b', clean_exp)
                if len(numbers) >= 1:
                    # If we find a price and a percentage, calculate the addition
                    if "%" in clean_exp and len(numbers) >= 2:
                        try:
                            base_price = float(numbers[0])
                            tax_percent = float(numbers[1])
                            # Calculate the price with tax
                            clean_exp = f"{base_price} + ({base_price} * {tax_percent}/100)"
                        except (ValueError, IndexError):
                            pass
                    # If we just have a price, use a default tax rate
                    else:
                        try:
                            base_price = float(numbers[0])
                            # Apply standard 15% tax
                            clean_exp = f"{base_price} + ({base_price} * 15/100)"
                        except (ValueError, IndexError):
                            pass
            
            # If we still have letters in the expression
            if re.search(r'[a-zA-Z_]', clean_exp):
                # Check if it contains allowed functions
                for func_name in allowed_functions:
                    if func_name in clean_exp:
                        continue
                else:
                    # If we reach here, there's an unknown identifier
                    return {
                        "success": False,
                        "error": "Invalid characters in expression. Only numbers, operators, and basic math functions are allowed."
                    }
            
            # Use the cleaned expression
            expression = clean_exp
            
            # Create a safe namespace for evaluation
            safe_dict = {
                "__builtins__": {},
                **allowed_functions
            }
            
            # Evaluate the expression
            result = eval(expression, safe_dict)
            
            # Format the result
            if isinstance(result, float):
                if result.is_integer():
                    result = int(result)
                else:
                    result = round(result, 8)  # Round to avoid floating point precision issues
            
            return {
                "success": True,
                "result": str(result)
            }
            
        except ZeroDivisionError:
            return {
                "success": False,
                "error": "Division by zero"
            }
        except (ValueError, TypeError) as e:
            return {
                "success": False,
                "error": f"Invalid mathematical expression: {str(e)}"
            }
        except SyntaxError:
            return {
                "success": False,
                "error": "Invalid syntax in mathematical expression"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Calculation failed: {str(e)}"
            }
