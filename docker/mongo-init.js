db.auth('mongocaplc', 'mongocaplc');

db = db.getSiblingDB('caplcDevDB');

db.createUser(
    {
        user: "caplc_user",
        pwd: "password123",
        roles: [
            {
                role: "readWrite",
                db: "caplcDevDB"
            }
        ]
    }
);

db = db.getSiblingDB('caplcTestDB');
db.createUser(
    {
        user: "caplc_user",
        pwd: "password123",
        roles: [
            {
                role: "readWrite",
                db: "caplcTestDB"
            }
        ]
    }
);
