const Telegraf = require('telegraf');
const bot = new Telegraf("286358309:AAG-NF68tQam6aN1PLCt0g1gm4kB5XS-Sic");

var VisualRecognitionV3 = require('watson-developer-cloud/visual-recognition/v3');
var fs = require('fs');

var visualRecognition = new VisualRecognitionV3({
    version: '2018-03-19',
    iam_apikey: 'UDDvweJSDR32NAZIfyxZ-dlvjIZ8dfRv75Z93xyjWGEX',
    url: "https://gateway.watsonplatform.net/visual-recognition/api"
});

var active_class = ""
var params = {
    classifier_id: 'dogs_1477088859'
};


function learn(pic_file) {
    params[active_class + "_examples"] = pic_file;
    visualRecognition.updateClassifier(params,
        function (err, response) {
            if (err) {
                console.log(err);
            } else {
                console.log(JSON.stringify(response, null, 2))
            }
        });
}


bot.start((message) => {
    console.log('started:', message.from.id)
    return message.reply('Hello my friend, contact me by send /contact, or write anything');
})

bot.hears('hi', message => {
    return message.reply('Hey!');
});

bot.command('learn', message => {
    return message.reply('Learn mode');
});

bot.command('recognize', message => {
    return message.reply('Recognize mode');
});

bot.on('sticker', (message) => {
    return message.reply('👍');
});

bot.on('text', message => {
    var text = message.message.text;

});

bot.on('photo', ({message, replyWithPhoto}) => {
    replyWithPhoto(message.photo.pop().file_id, {caption:'Your caption here'})
    bot.getFile(message.photo.pop().file_id);
    // return message.reply('A picture!');

});

bot.startPolling();
console.log("Bot running at https://telegram.me/sprintingkiwibot")