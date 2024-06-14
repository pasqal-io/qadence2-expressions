use crate::operator::Operator;
use crate::symbols::{Numerical,Symbol};

use std::ops::Add;
use num::Complex;


#[derive(Debug, PartialEq)]
pub enum Expression {
    Symbol(&'static str),
    Value(Numerical),
    Expr { head: Operator, args: Vec<Box<Expression>> },
}

// Implement helper functions to create different types of Expressions.
impl Expression {
    pub fn symbol(name: &'static str) -> Self {
        Expression::Symbol(name)
    }

    pub fn int(value: i64) -> Self {
        Expression::Value(Numerical::int(value))
    }

    pub fn float(value: f64) -> Self {
        Expression::Value(Numerical::float(value))
    }

    pub fn complex(real: f64, imag: f64) -> Self {
        Expression::Value(Numerical::complex(real, imag))
    }
}

impl Add for Expression {
    type Output = Expression;

    fn add(self, rhs: Self) -> Self::Output {
        // If both sides are Numerical, add them directly
        match (self, rhs) {
            (Expression::Value(lhs), Expression::Value(rhs)) => {
                Expression::Value(lhs + rhs)
            }
            // For other cases, create an Expression::Expr with Operator::Add
            (lhs, rhs) => Expression::Expr {
                head: Operator::ADD,
                args: vec![Box::new(lhs), Box::new(rhs)],
            },
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*; // This imports everything from the parent module

    #[test]
    fn test_symbol_expression() {
        let symbol_expr = Expression::symbol("x");
        assert_eq!(symbol_expr, Expression::Symbol("x"));
    }

    #[test]
    fn test_int_expression() {
        let int_expr = Expression::int(42);
        assert_eq!(int_expr, Expression::Value(Numerical::Int(42)));
    }

    #[test]
    fn test_float_expression() {
        let float_expr = Expression::float(3.14);
        assert_eq!(float_expr, Expression::Value(Numerical::Float(3.14)));
    }

    #[test]
    fn test_complex_expression() {
        let complex_expr = Expression::complex(1.0, 2.0);
        assert_eq!(complex_expr, Expression::Value(Numerical::Complex(Complex::new(1.0, 2.0))));
    }

    #[test]
    fn test_expression_add_int_to_int() {
        let expr1 = Expression::int(1);
        let expr2 = Expression::int(2);
        let result = expr1 + expr2;

	assert_eq!(result, Expression::Value(Numerical::Int(3)));
    }
    
    #[test]
    fn test_expression_add_int_to_float() {
        let expr1 = Expression::int(1);
        let expr2 = Expression::float(2.0);
        let result = expr1 + expr2;

	assert_eq!(result, Expression::Value(Numerical::Float(3.0)));
    }
  
    #[test]
    fn test_expression_add_int_to_complex() {
        let expr1 = Expression::int(1);
        let expr2 = Expression::complex(2.0, 4.0);
        let result = expr1 + expr2;

	assert_eq!(result, Expression::Value(Numerical::Complex(Complex::new(3.0, 4.0))));
    }
    
    #[test]
    fn test_expression_add_float_to_int() {
        let expr1 = Expression::float(1.0);
        let expr2 = Expression::int(2);
        let result = expr1 + expr2;

	assert_eq!(result, Expression::Value(Numerical::Float(3.0)));
    }
    
    #[test]
    fn test_expression_add_float_to_float() {
        let expr1 = Expression::float(1.0);
        let expr2 = Expression::float(2.0);
        let result = expr1 + expr2;

	assert_eq!(result, Expression::Value(Numerical::Float(3.0)));
    }

    #[test]
    fn test_expression_add_float_to_complex() {
        let expr1 = Expression::float(1.0);
        let expr2 = Expression::complex(2.0, 4.0);
        let result = expr1 + expr2;

	assert_eq!(result, Expression::Value(Numerical::Complex(Complex::new(3.0, 4.0))));
    }

    #[test]
    fn test_expression_add_complex_to_int() {
        let expr1 = Expression::complex(1.0, 2.0);
        let expr2 = Expression::int(2);
        let result = expr1 + expr2;

	assert_eq!(result, Expression::Value(Numerical::Complex(Complex::new(3.0, 2.0))));
    }
    
    #[test]
    fn test_expression_add_complex_to_float() {
        let expr1 = Expression::complex(1.0, 2.0);
        let expr2 = Expression::float(2.0);
        let result = expr1 + expr2;

	assert_eq!(result, Expression::Value(Numerical::Complex(Complex::new(3.0, 2.0))));
    }
    
    #[test]
    fn test_expression_add_complex_to_complex() {
        let expr1 = Expression::complex(1.0, 2.0);
        let expr2 = Expression::complex(3.0, 4.0);
        let result = expr1 + expr2;

	assert_eq!(result, Expression::Value(Numerical::Complex(Complex::new(4.0, 6.0))));
    }

    #[test]
    fn test_expression_add_symbol_to_int() {
        let symbol_expr = Expression::symbol("x");
        let expr2 = Expression::int(1);
        let result = symbol_expr + expr2;

	match result {
            Expression::Expr { head, args } => {
                assert_eq!(head, Operator::ADD);
                assert_eq!(*args[0], Expression::Symbol("x"));
                assert_eq!(*args[1], Expression::Value(Numerical::Int(1)));
            }
            _ => panic!("Expected an Expression::Expr with Operator::ADD"),
        }

    }
}
