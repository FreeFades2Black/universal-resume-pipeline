# ADR-0001: Intercepting HTMLInputElement Prototype Setter for React 16+ Controlled Components

**Status:** Accepted  
**Date:** 2026-05-24  
**Lead Architect:** William Free Hall (Free) <whall4.wh@gmail.com>

## 1. Context & Operational Challenge
Automating career application submissions across modern ATS platforms (Workday, Lever, Greenhouse) using headless browsers fails when setting input values via standard DOM methods (`element.value = "text"`). React's internal fiber state ignores direct DOM property mutations unless an `input` event bubbles through React's synthetic event wrapper.

## 2. Options Considered
* **Option A: Hardware Key Stroke Emulation (`page.keyboard.type`)**
  - *Evaluation:* Simulates real typing, but extremely slow (40-60 seconds per form) and prone to focus loss when unexpected modal popups appear.
* **Option B: Prototype Property Descriptor Interception with Synthetic Event Dispatch**
  - *Evaluation:* Calls `Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set.call(input, val)` followed by dispatching an untrusted `input` event with `{ bubbles: true }`.

## 3. Decision & Trade-Off Accepted
We adopted **Option B (Prototype Setter Interception)**.  
**Trade-Off Accepted:** Requires maintaining JavaScript polyfill snippets injected into the browser runtime context; reduces form autofill duration from 45 seconds to 1.2 seconds.
