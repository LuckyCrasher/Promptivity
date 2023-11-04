import 'emoji-log';
import {browser} from 'webextension-polyfill-ts';
import {initializeApp} from 'firebase/app';

const firebaseConfig = {
  apiKey: 'AIzaSyDQ9tyLAOWAyFwJQ1MJR0hWMiLRUOxmXBE',
  authDomain: 'promptivity-4e070.firebaseapp.com',
  projectId: 'promptivity-4e070',
  storageBucket: 'promptivity-4e070.appspot.com',
  messagingSenderId: '920655269130',
  appId: '1:920655269130:web:f56361f34047a91727bef3',
  measurementId: 'G-GE9BDGWHB6',
};

browser.runtime.onInstalled.addListener((): void => {
  console.emoji('🦄', 'extension installed');
  // console.log(Options);
  initializeApp(firebaseConfig);
});
