mod expression;
use expression::Operator;
mod symbols;
use symbols::Numeric;


fn main() {
    println!("Hello, world!");
    println!("{}", Operator::ADD.as_str());
}
