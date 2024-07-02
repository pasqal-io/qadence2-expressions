use num_traits::pow::Pow;

use crate::operator::Operator;
use crate::symbols::Numerical;

use std::ops::{Add, Div, Mul, Sub, Neg};


#[derive(Clone, Debug, PartialEq)]
pub enum Expression {
    Symbol(&'static str),
    Value(Numerical),
    Expr { head: Operator, args: Vec<Expression> },
}

// Implement helper functions to create different types of Expressions.
impl Expression {
    pub fn symbol(name: &'static str) -> Self {
        Expression::Symbol(name)
    }

    pub fn float(value: f64) -> Self {
        Expression::Value(Numerical::float(value))
    }

    pub fn complex(real: f64, imag: f64) -> Self {
        Expression::Value(Numerical::complex(real, imag))
    }
}

impl Neg for Expression {
    type Output = Expression;

    fn neg(self) -> Self::Output {
	use Expression::{Expr, Value, Symbol};
	use Operator::MUL;

	match self {
	    // Negating a symbol directly isn't well-defined, but for the sake of
	    // completeness, we could wrap it in an Expr with multiplication by -1.
	    Symbol(s) => Expr {
		head: MUL,
		args: vec![
		    Expression::float(-1.),
		    Expression::symbol(s),
		],
            },
	    
	    // Negate the numerical value.
	    Value(v) => {
		Value(-v)
	    },
	    
	    // Negate the entire expression by multiplying by -1
	    Expr { head, args } => Expr {
		head: MUL,
		args: vec![
		    Expression::float(-1.),
		    Expr {
			head,
			args,
		    }
		]	
	    },
	}
    }
}

impl Pow<Expression> for Expression {
    type Output = Expression;

    fn pow(self, rhs: Self) -> Self::Output {
	use Expression::{Expr, Value};
	use Operator::POW;

	match (self, rhs) {
            // Numerical values are operated directly.
            (Value(lhs), Value(rhs)) => Value(lhs.pow(rhs)),

            // If the left side is already a power expression, chain the exponent.
            (Expr { head: POW, args: mut args_lhs }, rhs) => {
                args_lhs.push(rhs);
                Expr { head: POW, args: args_lhs }
            },

            // Otherwise, create a new power expression.
            (lhs, rhs) => Expr {
                head: POW,
                args: vec![lhs, rhs],
            }
        }
    }
}

macro_rules! impl_binary_operator_for_expression {
   ($trait:ident, $method:ident, $operator:path) => {
       impl $trait for Expression {
          type Output = Self;

          fn $method(self, other: Self) -> Self {
             use Expression::*;

             match (self, other) {
                (Value(x), Value(y)) => Value(x.$method(y)),

                (Expr {head: $operator, args: args_lhs}, Expr {head: $operator, args: args_rhs}) => {
                   let args = args_lhs.into_iter().chain(args_rhs.into_iter()).collect();
                   Expr{head: $operator, args}
                },

                (Expr {head: $operator, args: mut args_lhs}, rhs) => {
                   args_lhs.push(rhs);
                   Expr {head: $operator, args: args_lhs}
                },

                (lhs, Expr {head: $operator, args: mut args_rhs}) => {
                   args_rhs.push(lhs);
                   Expr {head: $operator, args: args_rhs}
                },

                (lhs, rhs) => Expr{head: $operator, args: vec![lhs, rhs]},
             }
          }
       }
   };

   ($trait:ident, $method:ident, $operator:path, $inv:expr) => {
      impl $trait for Expression {
         type Output = Self;

         fn $method(self, other: Self) -> Self {
            use Expression::*;

            match (self, other) {
               (Value(x), Value(y)) => Value(x.$method(y)),
               (lhs, rhs) => Expr {
                  head: $operator,
                  args: vec![lhs, $inv(rhs)]
               },
            }
         }
      }
   }
}

impl_binary_operator_for_expression!(Add, add, Operator::ADD);
impl_binary_operator_for_expression!(Mul, mul, Operator::MUL);
impl_binary_operator_for_expression!(Sub, sub, Operator:: ADD, |x: Expression| { x.neg() });
impl_binary_operator_for_expression!(Div, div, Operator:: MUL, |x: Expression| { x.pow(Expression::float(-1.0)) });


#[cfg(test)]
mod tests {
    use super::*; // This imports everything from the parent module
    use num::Complex;
    use Expression::Expr;
    use Operator::{ADD, MUL};

    #[test]
    fn test_symbol_expression() {
        let symbol_expr = Expression::symbol("x");
        assert_eq!(symbol_expr, Expression::Symbol("x"));
    }

    #[test]
    fn test_neg_expression() {
        let expr = Expression::symbol("y");
        let neg_expr = -expr;
        assert_eq!(
            neg_expr,
            Expr {
                head: MUL,
                args: vec![
                    Expression::float(-1.),
                    Expression::symbol("y"),
                ]
            }
        );
    }
    
    #[test]
    fn test_float_expression() {
        let float_expr = Expression::float(3.14);
        assert_eq!(float_expr, Expression::Value(Numerical::Float(3.14)));
    }

    #[test]
    fn test_neg_float_expr() {
        let value = Expression::float(10.);
        let neg_value = -value;
        assert_eq!(neg_value, Expression::float(-10.));
    }

    #[test]
    fn test_complex_expression() {
        let complex_expr = Expression::complex(1.0, 2.0);
        assert_eq!(complex_expr, Expression::Value(Numerical::Complex(Complex::new(1.0, 2.0))));
    }

    #[test]
    fn test_neg_complex_expr() {
        let value = Expression::complex(1., 2.);
        let neg_value = -value;
        assert_eq!(neg_value, Expression::complex(-1., -2.));
    }
    
    #[test]
    fn test_mixed_types_expression_add() {
        let symbol_expr = Expression::symbol("x");
	let mixed_expr = Expression::float(1.) + symbol_expr;
        assert_eq!(
	    mixed_expr,
	    Expr {
		head: ADD,
		args: vec![
		    Expression::float(1.),
                    Expression::symbol("x"),
		]
	    }
	);
    }
    
    #[test]
    fn test_mixed_types_expression_sub() {
        let symbol_expr = Expression::symbol("x");
	let mixed_expr = Expression::complex(1.0, 2.0) - symbol_expr;
        assert_eq!(
	    mixed_expr,
	    Expr {
		head: ADD,
		args: vec![
		    Expression::complex(1.0, 2.0),
		    Expression::Expr {
			head: MUL,
			args: vec![
			    Expression::float(-1.),
			    Expression::symbol("x"),
			]
		    }
		]
	    }
	);
    }

    #[test]
    fn test_expression_binary_ops_float_to_float() {
        let expr1 = Expression::float(1.0);
        let expr2 = Expression::float(2.0);
        let n1 = expr1.clone() + expr2.clone();
        let n2 = expr1.clone() - expr2.clone();
        let n3 = expr1.clone() * expr2.clone();
        let n4 = expr1.clone() / expr2.clone();

	assert_eq!(n1, Expression::Value(Numerical::Float(3.0)));
	assert_eq!(n2, Expression::Value(Numerical::Float(-1.0)));
	assert_eq!(n3, Expression::Value(Numerical::Float(2.0)));
	assert_eq!(n4, Expression::Value(Numerical::Float(0.5)));
    }

    #[test]
    fn test_expression_binary_ops_float_to_complex() {
        let expr1 = Expression::float(1.0);
        let expr2 = Expression::complex(2.0, 4.0);
        let n1 = expr1.clone() + expr2.clone();
        let n2 = expr1.clone() - expr2.clone();
        let n3 = expr1.clone() * expr2.clone();
        let n4 = expr1.clone() / expr2.clone();

	assert_eq!(n1, Expression::Value(Numerical::Complex(Complex::new(3.0, 4.0))));
	assert_eq!(n2, Expression::Value(Numerical::Complex(Complex::new(-1.0, -4.0))));
	assert_eq!(n3, Expression::Value(Numerical::Complex(Complex::new(2.0, 4.0))));
	assert_eq!(n4, Expression::Value(Numerical::Complex(Complex::new(0.1, -0.2))));
    }

    #[test]
    fn test_expression_binary_ops_complex_to_float() {
        let expr1 = Expression::complex(1.0, 2.0);
        let expr2 = Expression::float(2.0);
        let n1 = expr1.clone() + expr2.clone();
        let n2 = expr1.clone() - expr2.clone();
        let n3 = expr1.clone() * expr2.clone();
        let n4 = expr1.clone() / expr2.clone();
	
	assert_eq!(n1, Expression::Value(Numerical::Complex(Complex::new(3.0, 2.0))));
	assert_eq!(n2, Expression::Value(Numerical::Complex(Complex::new(-1.0, 2.0))));
	assert_eq!(n3, Expression::Value(Numerical::Complex(Complex::new(2.0, 4.0))));
	assert_eq!(n4, Expression::Value(Numerical::Complex(Complex::new(0.5, 1.0))));
    }
    
    #[test]
    fn test_expression_add_complex_to_complex() {
        let expr1 = Expression::complex(1.0, 2.0);
        let expr2 = Expression::complex(3.0, 4.0);
        let n1 = expr1.clone() + expr2.clone();
        let n2 = expr1.clone() - expr2.clone();
        let n3 = expr1.clone() * expr2.clone();
        let n4 = expr1.clone() / expr2.clone();
	
	assert_eq!(n1, Expression::Value(Numerical::Complex(Complex::new(4.0, 6.0))));
	assert_eq!(n2, Expression::Value(Numerical::Complex(Complex::new(-2.0, -2.0))));
	assert_eq!(n3, Expression::Value(Numerical::Complex(Complex::new(-5.0, 10.0))));
	assert_eq!(n4, Expression::Value(Numerical::Complex(Complex::new(0.44, 0.08))));
    }
}
