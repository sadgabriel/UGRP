#!/usr/bin/env node

const SMALL_MIN = 9;
const SMALL_MAX = 16;
const SMALL_ROOM_MIN = 2;
const SMALL_ROOM_MAX = 7;
const SMALL_ROOM_IDEAL = 10;
const SMALL_RETRY = 100;

const LARGE_MIN = 16;
const LARGE_MAX = 30;
const LARGE_ROOM_MIN = 3;
const LARGE_ROOM_MAX = 9;
const LARGE_ROOM_IDEAL = 10;
const LARGE_RETRY = 100;


const fs = require('fs')
const path = require('path')
var roguelike = require(path.join(__dirname, "node-roguelike", "level", "roguelike"));

function getRandomInt(min, max) {
  min = Math.ceil(min);
  max = Math.floor(max);
  return Math.floor(Math.random() * (max - min + 1)) + min;
}

function divideArray(array, batchSize) {
  let result = [];
  for (let i = 0; i < array.length; i += batchSize) {
    let batch = array.slice(i, i + batchSize);
    result.push(batch);
  }
  return result;
}

function convertToString(level){
  let world = level.world;

  let stringMap = "";

  const tileMapping = {
    0: ' ',
    1: '.',
    2: '#',
    3: '/',
    4: 'X',
    5: '<',
    6: '>'
  };

  for (let y = 0; y < world.length; y++) {
    let row = '';
    for (let x = 0; x < world[y].length; x++) {
      let tile = world[y][x];
      row += tileMapping[tile] || tile;
    }
    stringMap += row + '\n';
  }

  return stringMap;
}

function createMap(width, height, roomMinWidth, roomMaxWidth, roomMinHeight, roomMaxHeight, roomIdeal, retry){

  let level = roguelike({
    width: width,
    height: height,
    retry: retry,
    special: false,
    room: {
      ideal: roomIdeal,
      min_width: roomMinWidth,
      max_width: roomMaxWidth,
      min_height: roomMinHeight,
      max_height: roomMaxHeight
    }
  });

  let stringMap = convertToString(level);

  let map = {
    params: {
      map_width: width,
      map_height: height,
      retry: retry,
      room_ideal: roomIdeal,
      room_min_width: roomMinWidth,
      room_max_width: roomMaxWidth,
      room_min_height: roomMinHeight,
      room_max_height: roomMaxHeight
    },
    map: stringMap
  }

  return map;
}

function createMaps(small, large){
  let maps = [];

  let error_count = 0;
  for (let i = 0; i < small; i++){
    let width = getRandomInt(SMALL_MIN, SMALL_MAX);
    let height = getRandomInt(SMALL_MIN, SMALL_MAX);
    
    try {
      var map = createMap(width, height, SMALL_ROOM_MIN, SMALL_ROOM_MAX, SMALL_ROOM_MIN, SMALL_ROOM_MAX, SMALL_ROOM_IDEAL, SMALL_RETRY);
    } catch {
      error_count++;
      if (error_count > 100){
        return maps;
      }
      i--;
      continue;
    }

    maps.push(map);
  }

  for (let i = 0; i < large; i++){
    let width = getRandomInt(LARGE_MIN, LARGE_MAX);
    let height = getRandomInt(LARGE_MIN, LARGE_MAX);

    try {
      var map = createMap(width, height, LARGE_ROOM_MIN, LARGE_ROOM_MAX, LARGE_ROOM_MIN, LARGE_ROOM_MAX, LARGE_ROOM_IDEAL, LARGE_RETRY);
    } catch {
      error_count++;
      if (error_count > 100){
        return maps;
      }
      i--;
      continue;
    }
    maps.push(map);
  }

  return maps;
}

function saveMaps(maps, prefix = "batch", batchSize = 100){
  batches = divideArray(maps, batchSize);
  let directoryName = path.join(path.dirname(__dirname), "data", "raw");

  if (!fs.existsSync(directoryName)) {
    fs.mkdirSync(directoryName, { recursive: true });
  }
  
  for (let i = 0; i < batches.length; i++){
    let jsonData =  JSON.stringify({"map_list": batches[i]}, null, 4);
    fs.writeFile(path.join(directoryName, `${prefix}${i}.json`), jsonData, (err) => {
      if (err) {
        console.error('An error occurred:', err);
        return;
      }
      console.log('JSON file has been saved.');
    });
  }
}

let maps = createMaps(100, 100);
saveMaps(maps);