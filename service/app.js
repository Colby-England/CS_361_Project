const express = require("express");
const app = express();
app.set('port', process.argv[2]);
app.use(express.json())

const defintions = {
    "Chest Press": "The bench press, or chest press, is an upper-body weight training exercise in which the trainee presses a weight upwards while lying on a weight training bench. The exercise uses the pectoralis major, the anterior deltoids, and the triceps, among other stabilizing muscles. A barbell is generally used to hold the weight, but a pair of dumbbells can also be used.",
    "Lat Pulldown": "The pull-down exercise is a strength training exercise designed to develop the latissimus dorsi muscle. It performs the functions of downward rotation and depression of the scapulae combined with adduction and extension of the shoulder joint.",
    "Pectoral Fly": "A fly or flye is a strength training exercise in which the hand and arm move through an arc while the elbow is kept at a constant angle. Flies are used to work the muscles of the upper body.",
    "Biceps Curl": "The term biceps curl refers to any of a number of weight training exercises that primarily targets the biceps brachii muscle. It may be performed using a barbell, dumbbell, resistance band, or other equipment.",
    "Triceps Press": "Lying triceps extensions, also known as skull crushers and French extensions or French presses, are a strength exercise used in many different forms of strength training. Lying triceps extensions are one of the most stimulating exercises to the entire triceps muscle group in the upper arm.",
    "Shoulder Press": "The overhead press (abbreviated OHP), also referred to as a shoulder press, military press, or simply the press, is a weight training exercise with many variations. It is typically performed while either standing or sitting sometimes also when squatting, in which a weight is pressed straight upwards from racking position until the arms are locked out overhead, while the legs, lower back and abs maintain balance.",
    "Row": "In strength training, rowing (or a row, usually preceded by a qualifying adjective — for instance a seated row) is an exercise where the purpose is to strengthen the muscles that draw the rower's arms toward the body (latissimus dorsi) as well as those that retract the scapulae (trapezius and rhomboids) and those that support the spine (erector spinae).",
    "Leg Press": "The leg press is a compound weight training exercise in which the individual pushes a weight or resistance away from them using their legs. The term leg press machine refers to the apparatus used to perform this exercise.",
    "Leg Extension": "The leg extension is a resistance weight training exercise that targets the quadriceps muscle in the legs. The exercise is done using a machine called the Leg Extension Machine.",
    "Leg Curl": "The leg curl, also known as the hamstring curl, is an isolation exercise that targets the hamstring muscles. The exercise involves flexing the lower leg against resistance towards the buttocks.",
    "Hip Abduction": "Hip abduction is the movement of the leg away from the midline of the body. The hip abductors are important and often forgotten muscles that contribute to our ability to stand, walk, and rotate our legs with ease.",
    "Hip Adduction": "Hip adductors are the muscles in your inner thigh that support balance and alignment. These stabilizing muscles are used to adduct the hips and thighs or move them toward the midline of your body."
}


app.get('/', (req, res) => {
    res.sendFile("C:/Users/engla/Desktop/OSU Online Comp Sci/2021_Summer/CS_361/Project/service/index.html")
})

// post route handles requests for the defined defintions of different workouts.
app.post('/', (req, res, next) => {

    let response = {}
    response['description'] = defintions[req.body.workout]

    res.send(JSON.stringify(response))
});

// error routes
app.use(function(req,res){
    res.status(404);
    // res.render('404');
  });
  
  app.use(function(err, req, res, next){
    console.error(err.stack);
    res.type('plain/text');
    res.status(500);
    // res.render('500');
  });

// listen on port specified with node index.js XXXX
app.listen(app.get('port'), () => {
    console.log(`Express started on port ${app.get('port')}`);
});