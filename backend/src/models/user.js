import mongoose from "mongoose";

const userschema = new mongoose.Schema({
        name : String,
        email: {
            type:String,
            unique: true
        },
        password: String
    },{ timestamps:true }
);

const User = mongoose.model("User",userschema);
export default User;