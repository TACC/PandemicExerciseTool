// LEGACY custom-expansion tests; preserved for rollback.
// // PET_COUNTY_FIXTURE points to a captured live table/dependency/asset response.
// const {test} = require('node:test');
// const assert = require('node:assert/strict');
// const fs = require('node:fs');
// const vm = require('node:vm');
// 
// test('served callback opens real 254-county rows through batched updates and redraws', {
//     skip: !process.env.PET_COUNTY_FIXTURE
// }, () => {
//     const fixture = JSON.parse(fs.readFileSync(process.env.PET_COUNTY_FIXTURE, 'utf8'));
//     const groups = {};
//     function visit(node) {
//         if (Array.isArray(node)) return node.forEach(visit);
//         if (!node || !node.props) return;
//         const id = node.props.id;
//         if (id && typeof id === 'object') (groups[id.type] ||= []).push(node.props);
//         visit(node.props.children);
//     }
//     visit(fixture.table);
//     assert.equal(groups['county-age-toggle'].length, 254);
//     assert.equal(fixture.dependency.inputs[0].property, 'n_clicks_timestamp');
// 
//     const noUpdate = {};
//     const context = {window: {dash_clientside: {no_update: noUpdate}}};
//     vm.runInNewContext(fixture.javascript, context);
//     const roots = {
//         'spread-table': {children: fixture.table},
//         'selected-state-store': {data: 'Texas'},
//         'county-age-history': {data: []},
//         'timeline-slider': {value: 0},
//         'view-toggle': {value: 'count'},
//         'selected-model-store': {data: 'seihrd-stochastic'},
//         'expanded-counties': {data: []},
//         'county-age-labels': {data: fixture.labels},
//         'county-age-click-state': {data: {state: null, timestamp: -1}},
//     };
//     const resultTargets = [
//         ['county-age-collapse', 'is_open'], ['county-age-toggle', 'children'],
//         ['county-age-toggle', 'aria-expanded'], ['county-age-toggle', 'aria-label'],
//         ['county-age-content', 'children'],
//     ];
//     function value(item) {
//         if (item.id.startsWith('{')) {
//             return groups[JSON.parse(item.id).type].map(props => props[item.property]);
//         }
//         return roots[item.id][item.property];
//     }
//     function run(triggers) {
//         // Use the real dependency order, rather than a hand-written argument list.
//         context.window.dash_clientside.callback_context = {triggered: triggers || []};
//         const args = [...fixture.dependency.inputs, ...fixture.dependency.state].map(value);
//         const output = context.window.dash_clientside.countyData.updateRow(...args);
//         assert.equal(output.length, 7);
//         resultTargets.forEach(([type, property], outputIndex) => {
//             assert.equal(output[outputIndex].length, groups[type].length);
//             output[outputIndex].forEach((val, index) => {
//                 if (val !== noUpdate) groups[type][index][property] = val;
//             });
//         });
//         if (output[5] !== noUpdate) roots['expanded-counties'].data = output[5];
//         if (output[6] !== noUpdate) roots['county-age-click-state'].data = output[6];
//         return output;
//     }
//     const openRows = () => groups['county-age-collapse'].filter(props => props.is_open);
//     run();
//     const first = groups['county-age-toggle'][130].id.fips;
//     groups['county-age-toggle'][130].n_clicks_timestamp = 100;
//     run([{prop_id: 'county-age-history.data'}, {
//         prop_id: JSON.stringify(groups['county-age-toggle'][130].id) + '.n_clicks_timestamp'
//     }]);
//     assert.equal(openRows().length, 1);
//     assert.equal(openRows()[0].id.fips, first);
//     assert.match(groups['county-age-content'][130].children.props.children, /Loading/);
// 
//     roots['county-age-history'].data = [fixture.ages];
//     run([{prop_id: 'county-age-history.data'}]);
//     assert.equal(openRows()[0].id.fips, first);
//     assert.equal(groups['county-age-content'][130].children.props.children[1].type, 'Table');
//     const second = groups['county-age-toggle'][131].id.fips;
//     groups['county-age-toggle'][131].n_clicks_timestamp = 200;
//     run([{prop_id: 'spread-table.children'}]);
//     assert.equal(openRows().length, 1);
//     assert.equal(openRows()[0].id.fips, second);
//     assert.equal(run()[5], noUpdate);
// 
//     // A server redraw reorders rows and resets button properties.
//     Object.values(groups).forEach(props => props.reverse());
//     groups['county-age-collapse'].forEach(props => { props.is_open = false; });
//     groups['county-age-toggle'].forEach(props => { props.n_clicks_timestamp = -1; });
//     run([{prop_id: 'spread-table.children'}]);
//     assert.equal(openRows().length, 1);
//     assert.equal(openRows()[0].id.fips, second);
// });
