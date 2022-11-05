// @generated automatically by Diesel CLI.

diesel::table! {
    messages (id) {
        id -> Integer,
        created_at -> Timestamp,
        filename -> Text,
        duration -> Integer,
        play_count -> Integer,
        last_played_at -> Nullable<Timestamp>,
    }
}
