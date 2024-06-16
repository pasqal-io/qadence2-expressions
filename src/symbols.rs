use num::Complex;
use std::ops::{Add, Div, Mul, Sub};
use std::fmt;


#[derive(Debug, PartialEq)]
pub enum Numerical {
    Int(i64),
    Float(f64),
    Complex(Complex<f64>),
}

impl Numerical {
    /// Convenience method to create a Numerical::Int
    pub fn int(value: i64) -> Self {
        Numerical::Int(value)
    }

    /// Convenience method to create a Numerical::Float
    pub fn float(value: f64) -> Self {
        Numerical::Float(value)
    }

    /// Convenience method to create a Numerical::Complex
    pub fn complex(re: f64, im: f64) -> Self {
        Numerical::Complex(Complex::new(re, im))
    }
}

impl fmt::Display for Numerical {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        match self {
            Numerical::Int(value) => write!(f, "{}", value),
            Numerical::Float(value) => write!(f, "{}", value),
            Numerical::Complex(value) => write!(f, "{} + {}i", value.re, value.im),
        }
    }
}

macro_rules! impl_binary_operator {
    ($binop:ident, $method:ident) => {
        impl $binop for Numerical {
            type Output = Self;
            
            fn $method(self, other: Self) -> Self {
                use Numerical::*;
                use num::Complex as complex;

                match (self, other) {
                    // Complex and Complex
                    (Complex(a), Complex(b)) => Complex(a.$method(b)),
                    
                    // Complex with Float or Int
                    (Complex(a), Float(b)) | (Float(b), Complex(a)) => Complex(a.$method(complex::from(b))),
                    (Complex(a), Int(b)) | (Int(b), Complex(a)) => Complex(a.$method(complex::from(b as f64))),
                    
                    // Float and Float
                    (Float(a), Float(b)) => Float(a.$method(b)),
                    
                    // Float with Int
                    (Float(a), Int(b)) => Float(a.$method(b as f64)),
                    (Int(a), Float(b)) => Float((a as f64).$method(b)),
                    
                    // Int and Int
                    (Int(a), Int(b)) => Int(a.$method(b)),
                }
            }
        }
    };
}

// Implement the binary operators for Numerical using the macro
impl_binary_operator!(Add, add);
impl_binary_operator!(Sub, sub);
impl_binary_operator!(Mul, mul);
impl_binary_operator!(Div, div);

#[derive(Debug, PartialEq)]
pub struct Symbol (&'static str);


#[cfg(test)]
mod tests {
    // Note this useful idiom: importing names from outer (for mod tests) scope.
    use super::*;

    #[test]
    fn test_numerical_add_int_to_int() {
        let n1 = Numerical::int(5);
        let n2 = Numerical::int(10);
        assert_eq!(n1 + n2, Numerical::int(15));
    }

    #[test]
    fn test_numerical_add_int_to_float() {
        let n1 = Numerical::int(5);
        let n2 = Numerical::float(10.5);
        assert_eq!(n1 + n2, Numerical::float(15.5));
    }
    
    #[test]
    fn test_numerical_add_int_to_complex() {
        let n1 = Numerical::int(5);
        let n2 = Numerical::complex(10.0, 5.0);
        assert_eq!(n1 + n2, Numerical::complex(15.0, 5.0));
    }

    #[test]
    fn test_numerical_add_float_to_int() {
        let n1 = Numerical::float(5.0);
        let n2 = Numerical::int(10);
        assert_eq!(n1 + n2, Numerical::float(15.0));
    }

    #[test]
    fn test_numerical_add_float_to_float() {
        let n1 = Numerical::float(5.0);
        let n2 = Numerical::float(10.0);
        assert_eq!(n1 + n2, Numerical::float(15.0));
    }
    
    #[test]
    fn test_numerical_add_float_to_complex() {
        let n1 = Numerical::float(5.0);
        let n2 = Numerical::complex(3.0, 4.0);
        assert_eq!(n1 + n2, Numerical::complex(8.0, 4.0));
    }
    
    #[test]
    fn test_numerical_add_complex_to_int() {
        let n1 = Numerical::complex(5.0, 4.0);
        let n2 = Numerical::int(3);
        assert_eq!(n1 + n2, Numerical::complex(8.0, 4.0));
    }
    
    #[test]
    fn test_numerical_add_complex_to_float() {
        let n1 = Numerical::complex(5.0, 4.0);
        let n2 = Numerical::float(3.0);
        assert_eq!(n1 + n2, Numerical::complex(8.0, 4.0));
    }

    #[test]
    fn test_numerical_add_complex_to_complex() {
        let n1 = Numerical::complex(5.0, 4.0);
        let n2 = Numerical::complex(3.0, 2.0);
        assert_eq!(n1 + n2, Numerical::complex(8.0, 6.0));
    }
    
    // #[test]
    // fn test_eq_int_and_float() {
    //     let n1 = Numerical::Int(5);
    //     let n2 = Numerical::Float(5.0);
    //     assert_eq!(n1, n2);
    // }

    // #[test]
    // fn test_eq_complex_and_int() {
    //     let n1 = Numerical::Complex(Complex::new(5.0, 0.0));
    //     let n2 = Numerical::Int(5);
    //     assert_eq!(n1, n2);
    // }

    
    // #[test]
    // fn test_numeric() {
    //     // assert_eq!(Numerical::Int(1)+Numerical::Int(2), Numerical::Int(2));
    //     // assert_eq!(Operator::MUL.as_str(), "*");
    //     // assert_eq!(Operator::NONCOMMUTE.as_str(), "@");
    //     // assert_eq!(Operator::POWER.as_str(), "^");
    //     // assert_eq!(Operator::CALL.as_str(), "call");
    // }
}
