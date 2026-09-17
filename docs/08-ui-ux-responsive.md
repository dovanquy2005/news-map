# UI/UX & Responsive Web

## Product principle

Map-first, information-dense but readable, mobile-first.

## Breakpoints

Use semantic breakpoints rather than device-specific hacks:

```text
mobile:   360–767px
tablet:   768–1023px
desktop:  >=1024px
wide:     >=1440px optional
```

## Desktop

```text
Header
----------------------------------
Map                    Event Feed
                         |
                         +-- Event card
                         +-- Event card
                         +-- Event card
----------------------------------
Legend / status
```

Event detail can appear as a right drawer/panel.

## Tablet

- map remains primary;
- feed becomes collapsible side panel;
- event detail uses drawer;
- controls must not cover essential map controls.

## Mobile

Map is full viewport.

Use:

- compact top search;
- filter drawer;
- bottom sheet for event popup/detail;
- swipe-friendly tabs;
- sticky action row only when useful.

Do not require hover.

## Touch targets

Interactive controls should be touch-friendly; avoid tiny markers/buttons.

## Accessibility

Minimum:

- keyboard navigation where possible;
- visible focus state;
- semantic buttons/links;
- contrast suitable for normal text;
- text alternative for marker details;
- not relying on color alone for status.

## Performance

- lazy load event detail;
- viewport-based event fetching;
- marker clustering;
- avoid thousands of React DOM nodes for markers;
- debounce search;
- virtualize long feed lists.

## State model

Keep URL-addressable state where useful:

```text
?from=&to=&province=&category=&event=&lat=&lng=&zoom=
```

Opening an event should be shareable through a stable event URL.
