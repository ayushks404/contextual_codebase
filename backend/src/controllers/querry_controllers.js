import query from "../models/query.js";


export const ask_ques = async (req,res) => {

    try{
        const { project_id, question } = req.body;

        if(!project_id|| !question){
            return res.status(400).json({
                message: "Project ID and question are required" 
            });
        }

        

        //sending query
        const airesponse = await axios.post("http://localhost:8000/query", {
            project_id,
            question
        });
        //get ans and sources as res 
        const res = {
            ans: airesponse.data.ans,
            sources: airesponse.data.sources
        };

        await query.create({
            project_id,
            userId: req.user.id,
            question,
            ans:res.ans,
            sources: result.sources
        });

        res.json({
            res
        });
    }

    catch (err){
        console.log("querry err", err.message);
        res.status(500).json({ message: "cant post querry or get res from ai "});
    }


};

