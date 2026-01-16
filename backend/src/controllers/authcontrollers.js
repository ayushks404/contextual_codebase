import User from "../models/user.js";
import jwt from "jsonwebtoken";
import bcrypt from "bcryptjs";

const generateToken = (id) => {
  return jwt.sign({ id }, process.env.JWT_SECRET, { expiresIn: "30d" });
};

export const register = async (req , res) => {

    try{
        const {name , email , password} = req.body;

        if (!name || !email || !password) {
            return res.status(400).json({ message: "Please provide all fields" });
        }
        const userExists = await User.findOne({ email });
        if (userExists) {
            return res.status(400).json({ message: "User already exists" });
        }

        const hashpassword = await bcrypt.hash(password , 10);

        const user = await User.create({
            name,
            email,
            password : hashpassword,
        });
        res.status(201).json({
            _id: user.id,
            name: user.name,
            email: user.email,
            token: generateToken(user.id),
        });

    } catch (err){
        res.status(500).json({
            message: err.message
        });
    }


};

export const login = async (req , res) => {

    try{
        const {email , password} = req.body;

        const user = await User.findOne({email});

        if(user){
                const match = await bcrypt.compare(password, user.password);

            if( match ){

                res.json({
                    _id : user.id,
                    name : user.name,
                    email : user.email,
                    token : generateToken(user.id),
                });
            }
            else{
                return res.status(401).json({ message: "Invalid credentials" });
            }

        }
        else{
            res.status(401).json({ 
                message: "Invalid email or password"
            });
        }
    }
    catch (err){
        res.status(500).json({
            message:err.message
        });
    }
};

