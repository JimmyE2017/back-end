mongo -- "$MONGO_INITDB_DATABASE" <<EOF
var user = '$MONGO_INITDB_ROOT_USERNAME';
var passwd = '$MONGO_INITDB_ROOT_PASSWORD';
var admin = db.getSiblingDB('admin');
admin.auth(user, passwd);
db = db.getSiblingDB('caplcDB');
db.createUser({user: "caplc_user",pwd: "password123",roles: [{role: "readWrite",db: "caplcDB"}]});
EOF