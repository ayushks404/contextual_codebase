import mongoose from "mongoose";

const queryschema = new mongoose.Schema({
       
    projectId : {
        type : mongoose.Schema.Types.ObjectId ,
        ref : "Project"
    },
    userId : {
        type : mongoose.Schema.Types.ObjectId,
        ref : "User"
    },
    question : {
        String
    },
    answer : {
        String
    },
    sources:{    //creating chunks of resources(like file name and line )
        Array
    }
        
    },{ timestamps:true }
);

const Query = mongoose.model("Query", queryschema);
export default Query;