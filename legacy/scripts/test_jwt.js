const crypto = require('crypto');

// Header
const header = {
    alg: 'HS256',
    typ: 'JWT'
};

// Calcular a data de expiração: hoje + 1 dia (24 horas)
const expirationDate = new Date();
expirationDate.setDate(expirationDate.getDate() + 1);
const exp = Math.floor(expirationDate.getTime() / 1000); // Timestamp Unix em segundos

// Body
const payload = {
    exp: exp
};

// Segredo
const secret = 't3hILevRdzfFyd05U2g+XT4lPZCmT6CB+ytaQljWWOk=';

const encodedHeader = Buffer.from(JSON.stringify(header))
    .toString('base64')
    .replace(/=/g, '')
    .replace(/\+/g, '-')
    .replace(/\//g, '_');

const encodedPayload = Buffer.from(JSON.stringify(payload))
    .toString('base64')
    .replace(/=/g, '')
    .replace(/\+/g, '-')
    .replace(/\//g, '_');

// Assinatura
const data = `${encodedHeader}.${encodedPayload}`;
const signature = crypto
    .createHmac('sha256', Buffer.from(secret, 'utf8'))
    .update(data)
    .digest('base64')
    .replace(/=/g, '')
    .replace(/\+/g, '-')
    .replace(/\//g, '_');

// Junte todas as partes
const jwt = `${encodedHeader}.${encodedPayload}.${signature}`;
console.log(jwt);
// exemplo de output: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NTM4OTM5OTN9.IxmRoSVQ8QlZX3tm1Dbar19ZUca70jYPHCDbM-7hP4E