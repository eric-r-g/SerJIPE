import express from 'express';
import { createRequire } from 'module';
const require = createRequire(import.meta.url);

const messages = require('./serjipe_message_pb.cjs');

const test = new messages.DeviceInfo();
test.setDeviceId('2');

const buffer = test.serializeBinary();
const test2 = messages.DeviceInfo.deserializeBinary(buffer);

console.log(test2.getDeviceId());

const app = express();

export default app;