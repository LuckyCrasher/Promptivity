import 'emoji-log';
import {browser} from 'webextension-polyfill-ts';

browser.runtime.onInstalled.addListener((): void => {
  console.emoji('🦄', 'extension installed');
});

// Called when tabs change
// browser.tabs.onUpdated.addListener((tabId, changeInfo, tab): void => {});
