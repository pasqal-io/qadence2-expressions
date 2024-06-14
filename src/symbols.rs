use num::Complex;
use std::ops::Add;
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

impl Add for Numerical {
    type Output = Numerical;

    fn add(self, rhs: Self) -> Self {
	match (self, rhs) {
	    (Numerical::Int(i1), Numerical::Int(i2)) => Numerical::Int(i1 + i2),
	    (Numerical::Int(i1), Numerical::Float(f2)) => Numerical::Float(i1 as f64 + f2),
	    (Numerical::Int(i1), Numerical::Complex(c2)) => Numerical::Complex(Complex::new(i1 as f64, 0.) + c2),
	    (Numerical::Float(f1), Numerical::Int(i2)) => Numerical::Float(f1 + i2 as f64),
	    (Numerical::Float(f1), Numerical::Float(f2)) => Numerical::Float(f1 + f2),
	    (Numerical::Float(f1), Numerical::Complex(c2)) => Numerical::Complex(Complex::new(f1, 0.) + c2),
	    (Numerical::Complex(c1), Numerical::Int(i2)) => Numerical::Complex(c1 + Complex::new(i2 as f64,0.)),
	    (Numerical::Complex(c1), Numerical::Float(f2)) => Numerical::Complex(c1 + Complex::new(f2, 0.)),
	    (Numerical::Complex(c1), Numerical::Complex(c2)) => Numerical::Complex(c1+c2),
 	}
    }
}

#[derive(Debug, PartialEq)]
pub struct Symbol (&'static str);


#[cfg(test)]
mod tests {
    // Note this useful idiom: importing names from outer (for mod tests) scope.
    use super::*;

    #[test]
    fn test_add_int_to_int() {
        let n1 = Numeric::int(5);
        let n2 = Numeric::int(10);
        assert_eq!(n1 + n2, Numeric::int(15));
    }

    #[test]
    fn test_add_int_to_float() {
        let n1 = Numeric::int(5);
        let n2 = Numeric::float(10.5);
        assert_eq!(n1 + n2, Numeric::float(15.5));
    }
    
    #[test]
    fn test_add_int_to_complex() {
        let n1 = Numeric::int(5);
        let n2 = Numeric::complex(10.0, 5.0);
        assert_eq!(n1 + n2, Numeric::complex(15.0, 5.0));
    }

    #[test]
    fn test_add_float_to_int() {
        let n1 = Numeric::float(5.0);
        let n2 = Numeric::int(10);
        assert_eq!(n1 + n2, Numeric::float(15.0));
    }

    #[test]
    fn test_add_float_to_float() {
        let n1 = Numeric::float(5.0);
        let n2 = Numeric::float(10.0);
        assert_eq!(n1 + n2, Numeric::float(15.0));
    }
    
    #[test]
    fn test_add_float_to_complex() {
        let n1 = Numeric::float(5.0);
        let n2 = Numeric::complex(3.0, 4.0);
        assert_eq!(n1 + n2, Numeric::complex(8.0, 4.0));
    }
    
    #[test]
    fn test_add_complex_to_int() {
        let n1 = Numeric::complex(5.0, 4.0);
        let n2 = Numeric::int(3);
        assert_eq!(n1 + n2, Numeric::complex(8.0, 4.0));
    }
    
    #[test]
    fn test_add_complex_to_float() {
        let n1 = Numeric::complex(5.0, 4.0);
        let n2 = Numeric::float(3.0);
        assert_eq!(n1 + n2, Numeric::complex(8.0, 4.0));
    }

    #[test]
    fn test_add_complex_to_complex() {
        let n1 = Numeric::complex(5.0, 4.0);
        let n2 = Numeric::complex(3.0, 2.0);
        assert_eq!(n1 + n2, Numeric::complex(8.0, 6.0));
    }
    
    // #[test]
    // fn test_eq_int_and_float() {
    //     let n1 = Numeric::Int(5);
    //     let n2 = Numeric::Float(5.0);
    //     assert_eq!(n1, n2);
    // }

    // #[test]
    // fn test_eq_complex_and_int() {
    //     let n1 = Numeric::Complex(Complex::new(5.0, 0.0));
    //     let n2 = Numeric::Int(5);
    //     assert_eq!(n1, n2);
    // }

    
    // #[test]
    // fn test_numeric() {
    //     // assert_eq!(Numeric::Int(1)+Numeric::Int(2), Numeric::Int(2));
    //     // assert_eq!(Operator::MUL.as_str(), "*");
    //     // assert_eq!(Operator::NONCOMMUTE.as_str(), "@");
    //     // assert_eq!(Operator::POWER.as_str(), "^");
    //     // assert_eq!(Operator::CALL.as_str(), "call");
    // }
}
