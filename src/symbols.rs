use num::Complex;
use num_traits::pow::Pow;
use std::ops::{Add, Div, Mul, Sub, Neg};
use std::fmt;



#[derive(Copy, Clone, Debug, PartialEq)]
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

impl Neg for Numerical {
    type Output = Numerical;
    
    fn neg(self) -> Self::Output {
	use Numerical::*;

	match self {
	    Int(i) => Numerical::int(-i),
	    Float(f) => Numerical::float(-f),
	    Complex(c) => Numerical::complex(-c.re, -c.im),
	}
    }
}

impl Pow<Numerical> for Numerical {
    type Output = Numerical;

    fn pow(self, rhs: Numerical) -> Self::Output {
        use Numerical::*;
	
        match (self, rhs) {
            (Int(base), Int(exp)) => Int((base as f64).powi(exp as i32) as i64),
            (Float(base), Int(exp)) => Float(base.powi(exp as i32)),
            (Complex(base), Int(exp)) => Complex(base.powi(exp as i32)),
            (Float(base), Float(exp)) => Float(base.powf(exp)),
            (Complex(base), Float(exp)) => Complex(base.powf(exp)),
            (Int(base), Float(exp)) => Float((base as f64).powf(exp)),
            (Complex(base), Complex(exp)) => Complex(base.powc(exp)),
            (Float(base), Complex(exp)) => Complex((num::Complex::new(base, 0.0)).powc(exp)),
            (Int(base), Complex(exp)) => Complex((num::Complex::new(base as f64, 0.0)).powc(exp)),
        }
    }
}

macro_rules! impl_binary_operator_for_numerical {
    ($trait:ident, $method:ident) => {
        impl $trait for Numerical {
            type Output = Self;
            
            fn $method(self, other: Self) -> Self::Output {
                use Numerical::*;
		// To disambiguate with the enum variant.
                use num::Complex as complex;

                match (self, other) {
                    // Complex and Complex
                    (Complex(a), Complex(b)) => Complex(a.$method(b)),
                    
                    // Complex with Float
                    (Complex(a), Float(b)) => Complex(a.$method(complex::from(b))),
                    (Float(a), Complex(b)) => Complex(complex::from(a).$method(b)),

		    // Complex with Int
                    (Complex(a), Int(b)) => Complex(a.$method(complex::from(b as f64))),
		    (Int(a), Complex(b)) => Complex(complex::from(a as f64).$method(b)),
                    
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
impl_binary_operator_for_numerical!(Add, add);
impl_binary_operator_for_numerical!(Sub, sub);
impl_binary_operator_for_numerical!(Mul, mul);
impl_binary_operator_for_numerical!(Div, div);

#[derive(Debug, PartialEq)]
pub struct Symbol (&'static str);

#[cfg(test)]
mod tests {
    // Note this useful idiom: importing names from outer (for mod tests) scope.
    use super::*;
    
    // Approximate equality check for Complex numbers
    fn approx_eq_complex(c1: &num::Complex<f64>, c2: &num::Complex<f64>, epsilon: f64) -> bool {
	(c1.re - c2.re).abs() < epsilon && (c1.im - c2.im).abs() < epsilon
    }

    #[test]
    fn test_negation_int() {
        let num_int = Numerical::Int(10);
        assert_eq!(-num_int, Numerical::Int(-10));

        let num_int_neg = Numerical::Int(-10);
        assert_eq!(-num_int_neg, Numerical::Int(10));
    }

    #[test]
    fn test_negation_float() {
        let num_float = Numerical::Float(5.5);
        assert_eq!(-num_float, Numerical::Float(-5.5));

        let num_float_neg = Numerical::Float(-5.5);
        assert_eq!(-num_float_neg, Numerical::Float(5.5));
    }

    #[test]
    fn test_negation_complex() {
        let num_complex = Numerical::Complex(Complex::new(3.0, 4.0));
        assert_eq!(-num_complex, Numerical::Complex(Complex::new(-3.0, -4.0)));

        let num_complex_neg = Numerical::Complex(Complex::new(-3.0, -4.0));
        assert_eq!(-num_complex_neg, Numerical::Complex(Complex::new(3.0, 4.0)));
    }

    #[test]
    fn test_numerical_pow() {
        let n1 = Numerical::Int(2);
        let n2 = Numerical::Int(3);
        assert_eq!(n1.pow(n2), Numerical::Int(8));

        let n3 = Numerical::Float(2.0);
        let n4 = Numerical::Float(3.0);
        assert_eq!(n3.pow(n4), Numerical::Float(8.0));

        let n5 = Numerical::Complex(num::Complex::new(2.0, 0.0));
        let n6 = Numerical::Complex(num::Complex::new(3.0, 0.0));
	if let Numerical::Complex(c) = n5.pow(n6) {
            assert!(approx_eq_complex(&c, &Complex::new(8.0, 0.0), 1e-9));
        } else {
            panic!("Expected complex result");
        }
    }

    #[test]
    fn test_numerical_binary_ops_int_to_int() {
        let n1 = Numerical::Int(5);
        let n2 = Numerical::Int(10);
        assert_eq!(n1 + n2, Numerical::Int(15));
        assert_eq!(n1 - n2, Numerical::Int(-5));
        assert_eq!(n1 * n2, Numerical::Int(50));
        assert_eq!(n1 / n2, Numerical::Int(0)); // integer division
    }

    #[test]
    fn test_numerical_binary_ops_int_to_float() {
	let n1 = Numerical::Int(5);
        let n2 = Numerical::Float(10.5);
        assert_eq!(n1 + n2, Numerical::Float(15.5));
        assert_eq!(n1 - n2, Numerical::Float(-5.5));
        assert_eq!(n1 * n2, Numerical::Float(52.5));
        assert_eq!(n1 / n2, Numerical::Float(5.0 / 10.5));
    }
    
    #[test]
    fn test_numerical_binary_ops_int_to_complex() {
        let n1 = Numerical::int(5);
        let n2 = Numerical::complex(10.0, 5.0);
        assert_eq!(n1 + n2, Numerical::Complex(Complex::new(15.0, 5.0)));
        assert_eq!(n1 - n2, Numerical::Complex(Complex::new(-5.0, -5.0)));
        assert_eq!(n1 * n2, Numerical::Complex(Complex::new(50.0, 25.0)));
        assert_eq!(n1 / n2, Numerical::Complex(Complex::new(0.4, -0.2)));
    }

    #[test]
    fn test_numerical_add_float_to_int() {
        let n1 = Numerical::float(5.0);
        let n2 = Numerical::int(10);
        assert_eq!(n1 + n2, Numerical::Float(15.0));
        assert_eq!(n1 - n2, Numerical::Float(-5.0));
        assert_eq!(n1 * n2, Numerical::Float(50.0));
        assert_eq!(n1 / n2, Numerical::Float(0.5));
    }

    #[test]
    fn test_numerical_binary_ops_float_to_float() {
        let n1 = Numerical::float(5.0);
        let n2 = Numerical::float(10.0);
        assert_eq!(n1 + n2, Numerical::Float(15.0));
        assert_eq!(n1 - n2, Numerical::Float(-5.0));
        assert_eq!(n1 * n2, Numerical::Float(50.0));
        assert_eq!(n1 / n2, Numerical::Float(0.5));
    }
    
    #[test]
    fn test_numerical_binary_ops_float_to_complex() {
        let n1 = Numerical::float(5.0);
        let n2 = Numerical::complex(3.0, 4.0);
        assert_eq!(n1 + n2, Numerical::Complex(Complex::new(8.0, 4.0)));
        assert_eq!(n1 - n2, Numerical::Complex(Complex::new(2.0, -4.0)));
        assert_eq!(n1 * n2, Numerical::Complex(Complex::new(15.0, 20.0)));
        assert_eq!(n1 / n2, Numerical::Complex(Complex::new(15.0 / 25.0, -20.0 / 25.0)));
    }
    
    #[test]
    fn test_numerical_binary_ops_complex_to_int() {
        let n1 = Numerical::complex(5.0, 4.0);
        let n2 = Numerical::int(3);
        assert_eq!(n1 + n2, Numerical::Complex(Complex::new(8.0, 4.0)));
        assert_eq!(n1 - n2, Numerical::Complex(Complex::new(2.0, 4.0)));
        assert_eq!(n1 * n2, Numerical::Complex(Complex::new(15.0, 12.0)));
        assert_eq!(n1 / n2, Numerical::Complex(Complex::new(5.0 / 3.0, 4.0 / 3.0)));
    }
    
    #[test]
    fn test_numerical_binary_ops_complex_to_float() {
        let n1 = Numerical::complex(5.0, 4.0);
        let n2 = Numerical::float(3.0);
        assert_eq!(n1 + n2, Numerical::Complex(Complex::new(8.0, 4.0)));
        assert_eq!(n1 - n2, Numerical::Complex(Complex::new(2.0, 4.0)));
        assert_eq!(n1 * n2, Numerical::Complex(Complex::new(15.0, 12.0)));
        assert_eq!(n1 / n2, Numerical::Complex(Complex::new(5.0 / 3.0, 4.0 / 3.0)));
    }

    #[test]
    fn test_numerical_binary_ops_complex_to_complex() {
        let n1 = Numerical::complex(5.0, 4.0);
        let n2 = Numerical::complex(3.0, 2.0);
        assert_eq!(n1 + n2, Numerical::Complex(Complex::new(8.0, 6.0)));
        assert_eq!(n1 - n2, Numerical::Complex(Complex::new(2.0, 2.0)));
        assert_eq!(n1 * n2, Numerical::Complex(Complex::new(7.0, 22.0)));
        assert_eq!(n1 / n2, Numerical::Complex(Complex::new(23.0 / 13.0, 2.0 / 13.0)));
    }

    
}
