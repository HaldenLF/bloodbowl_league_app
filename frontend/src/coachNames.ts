const FIRST_NAMES = [
  'Grubnak', 'Snagrot', 'Uzbag', 'Krudd', 'Thrakka', 'Gutrot', 'Skarg', 'Morgash', 'Rukk', 'Zagnutz',
  'Drogga', 'Nubgob', 'Gashnak', 'Wazgob', 'Brakka', 'Murg', 'Grimgut', 'Zogbit', 'Narzug', 'Bogrot',
]

const TITLES = [
  'Skullkrusha', 'Gutstompa', 'Bonebreaka', 'Tuffjaw', 'Ballsnatcha', 'Teefgrinda', 'Pitchwrecka',
  'Bigboot', 'Halfling-Flinga', 'Blitzbrakka', 'Red-Eye', 'Mudstompa', 'Snotkicka', 'Da Basha',
]

function pick(items: string[]): string {
  return items[Math.floor(Math.random() * items.length)]
}

export function randomCoachName(): string {
  return `${pick(FIRST_NAMES)} ${pick(TITLES)}`
}
