const mktex = function (id, value, name, deletable) {
	let r = document.createElement('input');
	r.id = id;
	r.setAttribute('type', 'text');
	r.setAttribute('value', value);
	let s = document.createElement('span')
	s.appendChild(document.createTextNode(name));
	s.appendChild(r);
	if (deletable) {
		let b = document.createElement("button")
		b.setAttribute('type', 'button');
		b.innerText = "Remove Match";
		b.addEventListener('click', function () {
			let nc = s.previousElementSibling;
			if (nc.tagName === 'BR') {
				console.log(nc)
				nc.parentElement.removeChild(nc)
			} else {
				console.log(nc.tagName)
			}
			s.parentElement.removeChild(s);
		});
		s.appendChild(b)
	}
	return s;
};
/**
  * Create a button element that calls a function when clicked.
  * @param {Function} func The function to call on click.
  * @param {string} text The text to display in the button
  * @returns {Element} The resulting button
  */
const simple_button = function (func, text) {
	let element = document.createElement('button')
	element.appendChild(document.createTextNode(text));
	element.addEventListener('click', func);
	element.setAttribute('type', 'button');
	return element;
};
/**
 * Create a button that deletes an element.
 * @param {Element} element The element to delete
 * @returns The button that deletes the element
 */
const delete_button = (element) => {
	let button = simple_button(function () {
		element.parentElement.removeChild(element);
	}, "-");

	button.addEventListener('mouseover', function () {
		element.classList.add('hovered');
	});
	button.addEventListener('mouseout', function () {
		element.classList.remove('hovered');
	});
	return button
};
/**
 * 
 * @param {Element} element The element whose display is toggled.
 * @returns {Element} The button that will toggle the display of the specified element.
 */
const toggle_visibility_button = function (element) {
	let l = simple_button(function () {
		let display = l.innerText === 'Hide' ? 'none' : '';
		l.innerText = (display === '' ? 'Show' : 'Hide');
		let current = l.nextSiblingElement;
		while (current) {
			current.style = 'display:' + display + ';';

			current = current.nextSiblingElement;
		}
	}, 'Hide');
	return l;
}
/**
 * Create a class matcher's interface elements given the json representation
 * @param {*} obj 
 * @returns {Element} The interface
 */
const class_matcher = function (obj) {
	let element = document.createElement("div");
	element.classList = ['simple-matcher'];
	element.appendChild(document.createTextNode('Window Class Matcher'))
	element.appendChild(document.createElement('br'))
	element.setAttribute('type', 'class');
	element.appendChild(delete_button(element))
	let matchers = document.createElement('div');
	matchers.setAttribute('class', 'matcher');
	let c = 0;
	if (!(obj['matcher'] instanceof Array)) {
		obj['matcher'] = [obj['matcher']];
	}
	for (const match of obj['matcher']) {
		matchers.appendChild(mktex('', match, 'Matches:', true));
		if (c !== obj['matcher'].length - 1) {
			matchers.appendChild(document.createElement('br'));
		}
		c++;
	}

	matchers.appendChild(simple_button(function () {
		matchers.insertBefore(document.createElement('br'),
			matchers.lastElementChild)
		matchers.insertBefore(mktex('', '', 'Matches'),
			matchers.lastElementChild)
	}, '+'))
	element.appendChild(matchers);
	element.appendChild(mktex('', obj['tags'].join(','), 'tags'))
	return element;
};
function from_name_matcher(form) {
	let tags = Array.from(form.getElementsByTagName('input')).map(function (f) { return f.value });
	let matchers = tags.slice(0, -1);
	return { 'type': form.getAttribute('type'), 'tags': tags[tags.length - 1].split(','), 'matcher': matchers };
}
const name_matcher = function (obj) {
	let element = document.createElement("div");
	element.classList = ['simple-matcher'];
	element.appendChild(document.createTextNode('Window Name Matcher'))
	element.appendChild(document.createElement('br'))
	element.setAttribute('type', 'name');
	element.appendChild(delete_button(element))
	let matchers = document.createElement('div');
	matchers.setAttribute('class', 'matcher');
	let c = 0;
	if (!(obj['matcher'] instanceof Array)) {
		obj['matcher'] = [obj['matcher']];
	} else {
		console.log(obj)
	}
	for (const match of obj['matcher']) {
		matchers.appendChild(mktex('', match, 'Matches:', true));
		if (c !== obj['matcher'].length - 1) {
			matchers.appendChild(document.createElement('br'));
		}

		c++;
	}
	matchers.appendChild(simple_button(function () {
		matchers.insertBefore(document.createElement('br'),
			matchers.lastElementChild)
		matchers.insertBefore(mktex('', '', 'Matches', true),
			matchers.lastElementChild)
	}, '+'));
	element.appendChild(matchers);
	element.appendChild(mktex('', obj['tags'].join(','), 'tags'))
	return element;
};
const add_matcher = function (element) {
	let first_one = undefined;
	let div = document.createElement("span");
	for (const name of ['name', 'class', 'or', 'and']) {
		let type = name;
		let l = simple_button(function (e) {
			let c = document.createElement("div");
			json_to_form(c, [{ 'type': type, 'matcher': [], 'tags': [] }]);
			console.log(first_one)
			for (const e of c.children) {

				element.insertBefore(e, div)
			}
		}, name);
		if (first_one === undefined)
			first_one = l

		div.appendChild(l);

	}
	element.appendChild(div);
}
/**
 * Generate a compound matcher's UI from a json object
 * @param {*} obj 
 * @returns 
 */
const compound = function (obj) {
	let element = document.createElement("div");
	element.appendChild(document.createTextNode(obj['type'] + ' Matcher'))
	element.appendChild(document.createElement('br'))
	element.setAttribute('type', obj['type']);
	element.appendChild(delete_button(element))
	element.classList = ['compound-matcher']
	let matchers = document.createElement('div');
	matchers.setAttribute('class', 'compound');
	let c = 0;
	json_to_form(matchers, obj['matcher'], true);
	let first_one = undefined;
	matchers.appendChild(simple_button(function () {
		matchers.insertBefore(document.createElement('br'),
			matchers.lastElementChild)
		matchers.insertBefore(mktex('', '', 'Matches'),
			matchers.lastElementChild)
	}, '+'));
	element.appendChild(matchers);
	element.appendChild(mktex('', obj['tags'].join(','), 'tags'))
	return element;
};
/**
 * Convert a compound element's form values into a json object representing the compound matcher
 * @param {*} form 
 * @returns 
 */
function from_compound(form) {

	let matchers = undefined;
	for (const i of form.children) {
		for (const cla of i.classList) {
			if (cla === 'compound') {
				matchers = i;
				break;
			}
		}
		if (matchers !== undefined) {
			break;
		}
	}
	return {
		'type': form.getAttribute('type'),
		'matcher': from_form(matchers)
	}
}
function json_to_form(form, data, add_buttons) {
	for (let e of data) {
		if (e['type'] === 'name') {
			form.appendChild(name_matcher(e));
		} else if (e['type'] === 'class') {
			form.appendChild(class_matcher(e))
		} else if (e['type'] === 'and' || e['type'] === 'or') {
			form.appendChild(compound(e));
		}
	}
	if (add_buttons)
		add_matcher(form);
}
function build_form(data) {
	let r = document.createElement('form');
	json_to_form(r, data)
	return r;
}
function from_form(form) {
	let l = [];
	for (const element of form.children) {
		let type = element.getAttribute('type');
		if (type === 'name' || type === 'class') {
			l.push(from_name_matcher(element));
		} else if (type === 'and' || type === 'or') {
			l.push(from_compound(element));
		}
	}
	return l;
}
