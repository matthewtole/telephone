use self::models::*;
use diesel::prelude::*;
use rust::*;

fn main() {
    use self::schema::messages::dsl::*;

    let connection = &mut establish_connection();
    let results = messages
        .filter(duration.eq(0))
        .limit(5)
        .load::<Message>(connection)
        .expect("Error loading posts");

    println!("Displaying {} posts", results.len());
    for post in results {
        println!("{:?}", post);
    }
}
