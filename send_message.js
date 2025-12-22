const archiver = require('archiver');
const FormData = require('form-data');
const axios = require('axios');
const { PassThrough } = require('stream');
const multer = require('multer');

// Настройка памяти для приема файлов
const upload = multer({ storage: multer.memoryStorage() });

// Функция-помощник для обработки файлов в Vercel
const runMiddleware = (req, res, fn) => {
    return new Promise((resolve, reject) => {
        fn(req, res, (result) => {
            if (result instanceof Error) return reject(result);
            return resolve(result);
        });
    });
};

export const config = {
    api: { bodyParser: false }, // Отключаем стандартный парсер, чтобы multer работал
};

export default async function handler(req, res) {
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
    if (req.method === 'OPTIONS') return res.status(200).end();

    try {
        // Запускаем multer для приема файлов из Tilda (поле files[])
        await runMiddleware(req, res, upload.array('files[]'));

        const { tid, message } = req.body;
        const files = req.files || []; 

        const form = new FormData();
        form.append('chat_id', process.env.TELEGRAM_CHAT_ID);

        if (files.length > 0) {
            const archive = archiver('zip', { zlib: { level: 9 } });
            const stream = new PassThrough();
            const chunks = [];

            stream.on('data', (chunk) => chunks.push(chunk));
            const zipFinished = new Promise((resolve, reject) => {
                stream.on('end', () => resolve(Buffer.concat(chunks)));
                stream.on('error', reject);
            });

            archive.pipe(stream);
            files.forEach(file => {
                archive.append(file.buffer, { name: file.originalname });
            });
            await archive.finalize();

            const buffer = await zipFinished;
            form.append('document', buffer, { filename: `nuvera_files_${tid}.zip` });
            if (message) form.append('caption', message);

            await axios.post(`https://api.telegram.org/bot${process.env.TELEGRAM_TOKEN}/sendDocument`, form, {
                headers: form.getHeaders(),
            });
        } else {
            await axios.post(`https://api.telegram.org/bot${process.env.TELEGRAM_TOKEN}/sendMessage`, {
                chat_id: process.env.TELEGRAM_CHAT_ID,
                text: message || "Пустое сообщение"
            });
        }

        return res.status(200).json({ success: true });
    } catch (error) {
        console.error('Ошибка:', error);
        return res.status(500).json({ error: error.message });
    }
}
