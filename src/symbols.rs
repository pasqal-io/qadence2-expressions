use num::Complex;
use std::ops::Add;


#[derive(Debug, PartialEq)]
pub enum Numeric {
    Int(i64),
    Float(f64),
    Complex(Complex<f64>),
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
    fn test_numeric() {
        // assert_eq!(Numeric::Int(1)+Numeric::Int(2), Numeric::Int(2));
        // assert_eq!(Operator::MUL.as_str(), "*");
        // assert_eq!(Operator::NONCOMMUTE.as_str(), "@");
        // assert_eq!(Operator::POWER.as_str(), "^");
        // assert_eq!(Operator::CALL.as_str(), "call");
    }
}
