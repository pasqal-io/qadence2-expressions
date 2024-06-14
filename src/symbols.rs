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

impl Add for Numeric {
    type Output = Numeric;

    fn add(self, rhs: Self) -> Self {
	match (self, rhs) {
	    (Numeric::Int(i1), Numeric::Int(i2)) => Numeric::Int(i1 + i2),
	    (Numeric::Int(i1), Numeric::Float(f2)) => Numeric::Float(i1 as f64 + f2),
	    (Numeric::Int(i1), Numeric::Complex(c2)) => Numeric::Complex(Complex::new(i1 as f64, 0.) + c2),
	    (Numeric::Float(f1), Numeric::Int(i2)) => Numeric::Float(f1 + i2 as f64),
	    (Numeric::Float(f1), Numeric::Float(f2)) => Numeric::Float(f1 + f2),
	    (Numeric::Float(f1), Numeric::Complex(c2)) => Numeric::Complex(Complex::new(f1,0.) + c2),
	    (Numeric::Complex(c1), Numeric::Int(i2)) => Numeric::Complex(c1 + Complex::new(i2 as f64,0.)),
	    (Numeric::Complex(c1), Numeric::Float(f2)) => Numeric::Complex(c1 + Complex::new(f2, 0.)),
	    (Numeric::Complex(c1), Numeric::Complex(c2)) => Numeric::Complex(c1+c2),
	    
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
