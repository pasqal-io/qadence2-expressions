use num_traits::pow::Pow;

use crate::operator::Operator;
use crate::symbols::Numerical;

use std::ops::{Add, Div, Mul, Sub, Neg};

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

impl Add for Expression {
    type Output = Expression;
    
    fn add(self, rhs: Self) -> Self::Output {
	use Expression::{Expr, Value};
	use Operator::ADD;
    
	match (self, rhs) {
	    // Numerical values are operated directly.
	    (Value(lhs), Value(rhs)) => Value(lhs + rhs),

	    // Both are Expressions with the same Operator::ADD, merge their arguments.
	    (Expr { head: ADD, args: args_lhs }, Expr { head: ADD, args: args_rhs }) => {
		let args = args_lhs.into_iter().chain(args_rhs).collect();
		Expr { head: ADD, args }
	    },

	    // Left side is an Expression with Operator::ADD, append the right side.
	    (Expr { head: ADD, args: mut args_lhs }, rhs) => {
		args_lhs.push(Box::new(rhs));
		Expr { head: ADD, args: args_lhs }
	    },

	    // Right side is an Expression with Operator::ADD, prepend the left side.
	    (lhs, Expr { head: ADD, args: mut args_rhs }) => {
		args_rhs.push(Box::new(lhs));
		Expr { head: ADD, args: args_rhs }
	    },

	    // Otherwise, create a new Expression::Expr with Operator::ADD.
	    (lhs, rhs) => Expr { head: ADD, args: vec![Box::new(lhs), Box::new(rhs)] },
	}
    }
}

impl Sub for Expression {
    type Output = Expression;
    
    fn sub(self, rhs: Self) -> Self::Output {
	use Expression::{Expr, Value};
	use Operator::{ADD, MUL};

	match (self, rhs) {
            // Numerical values are operated directly.
            (Value(lhs), Value(rhs)) => Value(lhs - rhs),

            // Transform x - y into Expr(Add, [x, Expr(Mul, [-1, y])])
            (lhs, rhs) => Expr {
                head: ADD,
                args: vec![
                    Box::new(lhs),
                    Box::new(Expr {
                        head: MUL,
                        args: vec![Box::new(Expression::int(-1)), Box::new(rhs)],
                    }),
                ],
            },
        }
    }
}

impl Mul for Expression {
    type Output = Expression;
    
    fn mul(self, rhs: Self) -> Self::Output {
	use Expression::{Expr, Value};
	use Operator::MUL;

	match (self, rhs) {
            // Numerical values are operated directly.
            (Value(lhs), Value(rhs)) => Value(lhs * rhs),

	    // Both are Expressions with the same Operator::MUL, merge their arguments.
	    (Expr { head: MUL, args: args_lhs }, Expr { head: MUL, args: args_rhs }) => {
		let args = args_lhs.into_iter().chain(args_rhs).collect();
		Expr { head: MUL, args }
	    },

	    // Left side is an Expression with Operator::MUL, append the right side.
	    (Expr { head: MUL, args: mut args_lhs }, rhs) => {
		args_lhs.push(Box::new(rhs));
		Expr { head: MUL, args: args_lhs }
	    },

	    // Right side is an Expression with Operator::MUL, prepend the left side.
	    (lhs, Expr { head: MUL, args: mut args_rhs }) => {
		args_rhs.push(Box::new(lhs));
		Expr { head: MUL, args: args_rhs }
	    },

	    // Otherwise, create a new Expression::Expr with Operator::MUL.
	    (lhs, rhs) => Expr { head: MUL, args: vec![Box::new(lhs), Box::new(rhs)] },
	}
    }
}



impl Div for Expression {
    type Output = Expression;
    
    fn div(self, rhs: Self) -> Self::Output {
	use Expression::{Expr, Value};
	use Operator::{MUL, POWER};

	match (self, rhs) {
            // Numerical values are operated directly.
            (Value(lhs), Value(rhs)) => Value(lhs / rhs),

            // Transform x / y into Expr(MUL, [x, Expr(POWER, [y, -1])])
            (lhs, rhs) => Expr {
                head: MUL,
                args: vec![
                    Box::new(lhs),
                    Box::new(Expr {
                        head: POWER,
                        args: vec![Box::new(rhs), Box::new(Expression::int(-1))],
                    }),
                ],
            },
        }
    }
}

// Macro to implement binary operators for the Expression enum
// macro_rules! impl_binary_operator_for_expression {
//     ($trait:ident, $method:ident, $operator:expr) => {
//         impl $trait for Expression {
//             type Output = Self;

//             fn $method(self, other: Self) -> Self::Output {
//                 use Expression::*;
//                 let operator = $operator;

//                 match (self, other) {
//                     // Numerical values are operated directly.
//                     (Value(lhs), Value(rhs)) => Value(lhs.$method(rhs)),

//                     // Both are Expressions with the same Operator::ADD, merge their arguments.
//                     (Expr { head: Operator::ADD, args: args_lhs }, Expr { head: Operator::ADD, args: args_rhs }) => {
//                         let args = args_lhs.into_iter().chain(args_rhs.into_iter()).collect();
//                         Expr { head: Operator::ADD, args }
//                     },

//                     // Left side is an Expression with Operator::ADD, append the right side.
//                     (Expr { head: Operator::ADD, args: mut args_lhs }, rhs) => {
//                         args_lhs.push(Box::new(rhs));
//                         Expr { head: Operator::ADD, args: args_lhs }
//                     },

//                     // Right side is an Expression with Operator::ADD, prepend the left side.
//                     (lhs, Expr { head: Operator::ADD, args: mut args_rhs }) => {
//                         args_rhs.push(Box::new(lhs));
//                         Expr { head: Operator::ADD, args: args_rhs }
//                     },

//                     // Otherwise, create a new Expression::Expr with the given operator.
//                     (lhs, rhs) => Expr { head: operator, args: vec![Box::new(lhs), Box::new(rhs)] },
//                 }
//             }
//         }
//     };
// }

// Applying the macro to implement Add, Sub, Mul, and Div for Expression
// impl_binary_operator_for_expression!(Add, add, Operator::ADD);
// impl_binary_operator_for_expression!(Sub, sub, Operator::SUB);
// impl_binary_operator_for_expression!(Mul, mul, Operator::MUL);
// impl_binary_operator_for_expression!(Div, div, Operator::DIV);




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
