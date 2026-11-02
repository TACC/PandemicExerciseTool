const {test} = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');
const context = {window: {}};
vm.runInNewContext(fs.readFileSync(path.join(__dirname, '../assets/epidemic_curve.js'), 'utf8'), context);
const {selectFrame} = context.window.dash_clientside.epidemicCurve;
const model = 'seirs-deterministic';
const events = Array.from({length: 300}, (_, day) => ({day, totalInfectedCount: day,
    counties: [{fips: '48201', ageGroups: ['large history']}]}));
const plain = value => JSON.parse(JSON.stringify(value));

test('initialization sends totals without counties or age data', () => {
    const output = selectFrame(events, 0, model, null);
    assert.equal(output.start, 0);
    assert.equal(output.points.length, 300);
    assert.equal(output.day, 0);
    assert.equal(output.points[1].totalInfectedCount, 1);
    assert.equal(JSON.stringify(output).includes('counties'), false);
    assert.equal(JSON.stringify(output).includes('ageGroups'), false);
});

test('only unacknowledged points are sent, including a batch of missed days', () => {
    const output = selectFrame(events, 299, model, {count: 297, model});
    assert.equal(output.start, 297);
    assert.deepEqual(plain(output.points.map(point => point.day)), [297, 298, 299]);
    assert.equal(output.day, 299);
});

test('scrubbing and repeat calls send no historical points after acknowledgment', () => {
    for (const timeline of [0, 150, 150, 299]) {
        const output = selectFrame(events, timeline, model, {count: 300, model});
        assert.equal(output.points.length, 0);
        assert.equal(output.day, timeline);
        assert.ok(JSON.stringify(output).length < 150);
    }
});

test('shortened history and changed models rebuild, empty history resets', () => {
    assert.equal(selectFrame(events.slice(0, 2), 0, model, {count: 300, model}).start, 0);
    assert.equal(selectFrame(events, 0, 'seihrd-stochastic', {count: 300, model}).start, 0);
    const empty = selectFrame([], 0, model, {count: 300, model});
    assert.equal(empty.start, 0);
    assert.equal(empty.count, 0);
    assert.equal(empty.day, null);
});

test('invalid timeline hides marker and valid index uses the actual simulation day', () => {
    assert.equal(selectFrame(events, null, model, null).day, null);
    assert.equal(selectFrame(events, 500, model, null).day, null);
    assert.equal(selectFrame([{day: 10}], 0, model, null).day, 10);
});
