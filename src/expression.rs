use num_traits::pow::Pow;

use crate::operator::Operator;
use crate::symbols::Numerical;

use std::ops::{Add, Div, Mul, Sub, Neg};

#[macro_export]
macro_rules! vbox {
   () => { vec![] };
   ($($x:expr),+ $(,)?) => { vec![$(Box::new($x)),*] };
}

#[derive(Clone, Debug, PartialEq)]
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
		args: vbox![
		    Expression::int(-1),
		    Expression::symbol(s),
		]
	    },
	    
	    // Negate the numerical value.
	    Value(v) => {
		Value(-v)
	    },
	    
	    // Negate the entire expression by multiplying by -1
	    Expr { head, args } => Expr {
		head: MUL,
		args: vbox![
		    Expression::int(-1),
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
                args_lhs.push(Box::new(rhs));
                Expr { head: POW, args: args_lhs }
            },

            // Otherwise, create a new power expression.
            (lhs, rhs) => Expr {
                head: POW,
                args: vbox![lhs, rhs],
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
                   args_lhs.push(Box::new(rhs));
                   Expr {head: $operator, args: args_lhs}
                },

                (lhs, Expr {head: $operator, args: mut args_rhs}) => {
                   args_rhs.push(Box::new(lhs));
                   Expr {head: $operator, args: args_rhs}
                },

                (lhs, rhs) => Expr{head: $operator, args: vbox![lhs, rhs]},
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
                  args: vbox![lhs, $inv(rhs)]
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
    fn test_mixed_types_expression_add() {
        let symbol_expr = Expression::symbol("x");
	let mixed_expr = Expression::int(1) + symbol_expr;
        assert_eq!(
	    mixed_expr,
	    Expression::Expr {
		head: Operator::ADD,
		args: vec![
		    Box::new(Expression::int(1)),
                    Box::new(Expression::symbol("x")),
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
	    Expression::Expr {
		head: Operator::ADD,
		args: vec![
		    Box::new(Expression::complex(1.0, 2.0)),
                    Box::new(
			Expression::Expr {
			    head: Operator::MUL,
			    args: vec![
				Box::new(Expression::int(-1)),
				Box::new(Expression::symbol("x")),
			    ]
			}
		    ),
		]
	    }
	);
    }

    #[test]
    fn test_numerical_binary_ops() {
        let n1 = Expression::int(10);
        let n2 = Expression::int(3);
        assert_eq!(n1.clone() + n2.clone(), Expression::int(13));
        assert_eq!(n1.clone() - n2.clone(), Expression::int(7));
        assert_eq!(n1.clone() * n2.clone(), Expression::int(30));
        assert_eq!(n1 / n2, Expression::int(3));
    }

    // #[test]
    // fn test_expression_add_int_to_int() {
    //     let expr1 = Expression::int(1);
    //     let expr2 = Expression::int(2);
    //     let result = expr1 + expr2;

    // 	assert_eq!(result, Expression::Value(Numerical::Int(3)));
    // }
    
    // #[test]
    // fn test_expression_add_int_to_float() {
    //     let expr1 = Expression::int(1);
    //     let expr2 = Expression::float(2.0);
    //     let result = expr1 + expr2;

    // 	assert_eq!(result, Expression::Value(Numerical::Float(3.0)));
    // }
  
    // #[test]
    // fn test_expression_add_int_to_complex() {
    //     let expr1 = Expression::int(1);
    //     let expr2 = Expression::complex(2.0, 4.0);
    //     let result = expr1 + expr2;

    // 	assert_eq!(result, Expression::Value(Numerical::Complex(Complex::new(3.0, 4.0))));
    // }
    
    // #[test]
    // fn test_expression_add_float_to_int() {
    //     let expr1 = Expression::float(1.0);
    //     let expr2 = Expression::int(2);
    //     let result = expr1 + expr2;

    // 	assert_eq!(result, Expression::Value(Numerical::Float(3.0)));
    // }
    
    // #[test]
    // fn test_expression_add_float_to_float() {
    //     let expr1 = Expression::float(1.0);
    //     let expr2 = Expression::float(2.0);
    //     let result = expr1 + expr2;

    // 	assert_eq!(result, Expression::Value(Numerical::Float(3.0)));
    // }

    // #[test]
    // fn test_expression_add_float_to_complex() {
    //     let expr1 = Expression::float(1.0);
    //     let expr2 = Expression::complex(2.0, 4.0);
    //     let result = expr1 + expr2;

    // 	assert_eq!(result, Expression::Value(Numerical::Complex(Complex::new(3.0, 4.0))));
    // }

    // #[test]
    // fn test_expression_add_complex_to_int() {
    //     let expr1 = Expression::complex(1.0, 2.0);
    //     let expr2 = Expression::int(2);
    //     let result = expr1 + expr2;

    // 	assert_eq!(result, Expression::Value(Numerical::Complex(Complex::new(3.0, 2.0))));
    // }
    
    // #[test]
    // fn test_expression_add_complex_to_float() {
    //     let expr1 = Expression::complex(1.0, 2.0);
    //     let expr2 = Expression::float(2.0);
    //     let result = expr1 + expr2;

    // 	assert_eq!(result, Expression::Value(Numerical::Complex(Complex::new(3.0, 2.0))));
    // }
    
    // #[test]
    // fn test_expression_add_complex_to_complex() {
    //     let expr1 = Expression::complex(1.0, 2.0);
    //     let expr2 = Expression::complex(3.0, 4.0);
    //     let result = expr1 + expr2;

    // 	assert_eq!(result, Expression::Value(Numerical::Complex(Complex::new(4.0, 6.0))));
    // }

    // #[test]
    // fn test_expression_add_symbol_to_int() {
    //     let symbol_expr = Expression::symbol("x");
    //     let expr2 = Expression::int(1);
    //     let result = symbol_expr + expr2;

    // 	match result {
    //         Expression::Expr { head, args } => {
    //             assert_eq!(head, Operator::ADD);
    //             assert_eq!(*args[0], Expression::Symbol("x"));
    //             assert_eq!(*args[1], Expression::Value(Numerical::Int(1)));
    //         }
    //         _ => panic!("Expected an Expression::Expr with Operator::ADD"),
    //     }

    // }
}
