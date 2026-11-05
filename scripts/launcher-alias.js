#!/usr/bin/env node
const fs = require('fs');
const path = require('path');
module.exports = function (context) {
  const manifest = path.join(context.opts.projectRoot, 'platforms/android/app/src/main/AndroidManifest.xml');
  if (!fs.existsSync(manifest)) return;
  let xml = fs.readFileSync(manifest, 'utf8');
  const activity = xml.match(/<activity\b[^>]*android:name="MainActivity"[^>]*>[\s\S]*?<\/activity>/);
  if (!activity) throw new Error('MainActivity not found; cannot safely configure icon aliases');
  const cleaned = activity[0].replace(/<intent-filter\b[^>]*>[\s\S]*?<\/intent-filter>/g, block =>
    block.includes('android.intent.action.MAIN') && block.includes('android.intent.category.LAUNCHER') ? '' : block);
  if (!xml.includes('Icon_default')) throw new Error('Icon aliases missing; refusing to remove launcher');
  xml = xml.replace(activity[0], cleaned);
  fs.writeFileSync(manifest, xml);
};
