#!/usr/bin/env node

/**
 * 의사코드
 * def createMap():
 *  여러 매개 변수를 받아 맵 객체를 반환한다.
 *  보다 직접적인 파라미터를 받는다. 
 * 
 * def createMaps():
 *  매개 변수를 받아 맵 객체의 리스트를 반환한다.
 *  보다 추상적인 파라미터를 받는다.
 *  파일 최상단의 상수 부분에 있는 값들을 가져와서 쓴다. 각 맵 크기에 따른 설정들.
 *  작은 맵, 중간 맵, 큰 맵을 만드는 과정을 거친다. 만드는 건 createMap으로 만든다.
 * 
 * def saveMaps():
 *  맵의 리스트와 저장될 경로를 받아 맵을 저장한다.
 * 
 * def convertToString():
 *  node roguelike가 만든 맵을 문자열 형태로 바꿔서 반환한다.
 */

const fs = require('fs')
var roguelike = require('../roguelike/node_modules/roguelike/level/roguelike');

const fileStream = fs.createWriteStream('input/test_map3.txt');

var level = roguelike({
  width: 31,
  height: 19,
  retry: 100,
  special: false,
  room: {
    ideal: 11,
    min_width: 3,
    max_width: 9,
    min_height: 3,
    max_height: 9
  }
});

var world = level.world;

// Crude mechanism for drawing level
for (var y = 0; y < world.length; y++) {
  var row = '';
  for (var x = 0; x < world[y].length; x++) {
    var tile = world[y][x];
    if (tile === 0) {
      row += ' ';
    } else if (tile === 1) {
      row += '.';
    } else if (tile === 2) {
      row += '#';
    } else if (tile === 3) {
      row += '/';
    } else if (tile === 4) {
      row += 'X';
    } else if (tile === 5) {
      row += '<';
    } else if (tile === 6) {
      row += '>';
    } else {
      row += world[y][x];
    }
  }

  fileStream.write(row + '\n');
}

