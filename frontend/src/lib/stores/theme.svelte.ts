type Theme = 'light' | 'dark';

const STORAGE_KEY = 'mauekspor-theme';

function getBrowserTheme(): Theme {
	if (typeof window === 'undefined') return 'light';
	return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
}

function getInitial(): Theme {
	if (typeof window === 'undefined') return 'light';
	const saved = window.localStorage.getItem(STORAGE_KEY);
	if (saved === 'light' || saved === 'dark') return saved;
	return getBrowserTheme();
}

function apply(theme: Theme) {
	document.documentElement.classList.toggle('dark', theme === 'dark');
}

let theme = $state<Theme>(getInitial());

export function getTheme() {
	return theme;
}

export function setTheme(next: Theme) {
	theme = next;
	window.localStorage.setItem(STORAGE_KEY, next);
	apply(next);
}

export function toggleTheme() {
	setTheme(theme === 'dark' ? 'light' : 'dark');
}

// Sync with the browser default when the user has not saved a preference.
if (typeof window !== 'undefined') {
	window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (event) => {
		const saved = window.localStorage.getItem(STORAGE_KEY);
		if (saved === 'light' || saved === 'dark') return;
		theme = event.matches ? 'dark' : 'light';
		apply(theme);
	});
}
