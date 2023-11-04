import 'emoji-log';
import { browser } from 'webextension-polyfill-ts';
browser.runtime.onInstalled.addListener(function () {
    console.emoji('🦄', 'extension installed');
});
