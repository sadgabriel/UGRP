#!/usr/bin/env node

const tileMapping = {
    0: ' ',
    1: '.',
    2: '#',
    3: '/',
    4: 'X',
    5: '<',
    6: '>'
};

const fs = require('fs');
const path = require('path');
const yaml = require('js-yaml');

const file = fs.readFileSync(path.join(__dirname, 'config.yaml'), 'utf8');
const config = yaml.load(file);

var roguelike = require(path.join("..", "src", "node-roguelike", "level", "roguelike"));

function convertToString(level){
    let world = level.world;
  
    let stringMap = "";
  
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

function createNodeMap(mapSize, roomSizeMin, roomSizeMax, roomCountIdeal){
    while (true){
        let error_count = 0;
        try {
            let level = roguelike({
                width: mapSize + 1,
                height: mapSize + 1,
                retry: 100,
                special: false,
                room: {
                ideal: roomCountIdeal,
                min_width: roomSizeMin,
                max_width: roomSizeMax,
                min_height: roomSizeMin,
                max_height: roomSizeMax
                }
            });

            return level;
        } catch{
            error_count++;
            if (error_count > 10){
                console.log("Too many errors occured while creating maps.");
                return null;
            }
        }
    }
}

function checkMapSize(map, mapSize){
    map = map.replace(/\n/g, "");

    if (map.length != (mapSize + 1) * (mapSize + 1)) {
        console.log("Invalid map or mapSize.");
        return false;
    }

    let topOK = false;
    let bottomOK = false;
    let leftOK = false;
    let rightOK = false;

    for (let i = 0; i < mapSize; ++i){
        if (map[i] == "#") topOK = true;
        if (map[(mapSize + 1) * (mapSize - 1) + i] == "#") bottomOK = true;
        if (map[(mapSize + 1) * i] == "#") leftOK = true;
        if (map[(mapSize + 1) * i + (mapSize - 1)] == "#") rightOK = true;
    }

    return topOK && bottomOK && leftOK && rightOK;
}

function createMap(mapSize, roomCountIdeal){
    let roomSizeMin = 3;
    let roomSizeMax = mapSize - 4;

    let running = true;
    while (running){
        roomSizeMax--;

        if (roomSizeMax == 3){
            break;
        }

        for (let i = 0; i < 3; ++i){
            let level = createNodeMap(mapSize, roomSizeMin, roomSizeMax, roomCountIdeal);
    
            if (level["room_count"] == roomCountIdeal){
                running = false;
            }
        }
    }

    while (1){
        let level = createNodeMap(mapSize, roomSizeMin, roomSizeMax, roomCountIdeal);

        if (level["room_count"] != roomCountIdeal) continue;

        let stringMap = convertToString(level);
        
        if (!checkMapSize(stringMap, mapSize)) continue;

        return stringMap;
    }
}

function emptyDirectory(dirPath) {
    const files = fs.readdirSync(dirPath);
  
    for (const file of files) {
        const fullPath = path.join(dirPath, file);
        if (fs.lstatSync(fullPath).isDirectory()) {
            emptyDirectory(fullPath);
            fs.rmdirSync(fullPath);
        } else {
            fs.unlinkSync(fullPath);
        }
    }
}

let mapSize;
let roomCountIdeal;
let mapCount;

if (process.argv.length >= 5){
    const args = process.argv.slice(2);
    mapSize = Number(args[0]);
    roomCountIdeal = Number(args[1]);
    mapCount = Number(args[2]);
} else {
    console.log("Not enough parameters.");
    process.exit();
}

let directoryName = path.join(__dirname, config["paths"]["raw"]);

if (!fs.existsSync(directoryName)) {
    fs.mkdirSync(directoryName, { recursive: true });
}

emptyDirectory(directoryName);

let mapList = [];
for (let i = 0; i < mapCount; ++i){
    mapList.push({"params": {}, "map": createMap(mapSize, roomCountIdeal)});
}

data = {"map_list": mapList};

const jsonData = JSON.stringify(data, null, 2);

fs.writeFile(path.join(directoryName, 'rawMaps.json'), jsonData, (err) => {
  if (err) {
    console.error('An error occurred:', err);
  } else {
    console.log('File has been saved');
  }
});

