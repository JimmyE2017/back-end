db.auth('mongocaplc', 'mongocaplc');

db = db.getSiblingDB('caplcDB');

db.createUser(
    {
        user: "caplc_user",
        pwd: "password123",
        roles: [
            {
                role: "readWrite",
                db: "caplcDB"
            }
        ]
    }
);
