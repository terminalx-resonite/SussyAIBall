import express from 'express';
import ffmpeg from 'fluent-ffmpeg'
import fs from 'fs'
import { randomUUID } from 'crypto';

//pre inits
 const app = express();
 const url = process.env.URL;
 const port = process.env.PORT;
// const errdir = process.env.ERROR_DIRECTORY;
// const errsound = process.env.ERROR_SOUND;
 const playdir = process.env.PLAY_DIRECTORY;

// if(!url  && !port && !errdir && !errsound && !playdir)
// {
//     console.log("Check your config shit broken!");
//     process.kill(1, "Invalid config.");
// }

//string formats

const playurl = `${url}:${port}/${playdir}/`;

app.post('/tts', (req, res) => {
    var text = req.query.txt;

    if(!text) return res.status(500).send("Hello. Sorry we cannot do that request since you really have not given much to go on. you dingus.")
    res.status(200).send(generateTTS(res, text));
})

app.use('/play', express.static('storage'));

app.listen(3000)



function generateTTS(res, text) {
    let uuid = randomUUID();
    let url = `http://185.130.224.61:5000/api/v1/chat`;
    let data = {
        "user_input": text,
        "max_new_tokens": 250,
        "auto_max_new_tokens": false,
        "max_tokens_second": 0,
        "history": {"internal": [], "visible": []},
        "mode": "instruct",
        "character": "Example",
        "instruction_template": "Vicuna-v1.1",
        "your_name": "You",
        "regenerate": false,
        "_continue": false,
        "chat_instruct_command": "Continue the chat dialogue below. Write a single reply for the character \"\".\n\n",
        "preset": "None",
        "do_sample": true,
        "temperature": 0.7,
        "top_p": 0.1,
        "typical_p": 1,
        "epsilon_cutoff": 0,
        "eta_cutoff": 0,
        "tfs": 1,
        "top_a": 0,
        "repetition_penalty": 1.18,
        "repetition_penalty_range": 0,
        "top_k": 40,
        "min_length": 0,
        "no_repeat_ngram_size": 0,
        "num_beams": 1,
        "penalty_alpha": 0,
        "length_penalty": 1,
        "early_stopping": false,
        "mirostat_mode": 0,
        "mirostat_tau": 5,
        "mirostat_eta": 0.1,
        "grammar_string": "",
        "guidance_scale": 1,
        "negative_prompt": "",
        "seed": -1,
        "add_bos_token": true,
        "truncation_length": 2048,
        "ban_eos_token": false,
        "custom_token_bans": "",
        "skip_special_tokens": true,
        "stopping_strings": []
    };
    fetch(
        url,
        {
            method: 'POST',
            headers: { 'Accept': 'application/json' },
            body: data
        }
    ).then(res => {
        new Promise((resolve, reject) => {
            const dest = fs.createWriteStream(__dirname + `/storage/${uuid}.ogg`);
            res.body.pipe(dest);
            res.body.on('end', () => resolve());
            dest.on('error', reject);
        })
    });

    setTimeout(() => {
        convert(__dirname + `/storage/` + uuid + `.wav`, __dirname + "/storage/" + uuid + ".ogg")
    }, 500);
    res.send(playurl + uuid + `.ogg`)
    setTimeout(() => {
        fs.unlink(__dirname + `/storage/` + uuid + `.wav`, function () { });
    }, 2000);

    setTimeout(() => {
        fs.unlink(__dirname + `/storage/` + uuid + `.ogg`, function () { });
    }, 1000 * 60);

    return playurl;
}

function convert(input, output) {
    ffmpeg(input)
        .output(output)
        .on('end', function () {
            console.log('conversion ended');
        }).on('error', (e) => {
            console.log(e);
        }).run();
}