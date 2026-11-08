/*
 * Optional Xiaoxun advertising-response cleanup.
 * Copyright (C) 2026 Vtous
 * SPDX-License-Identifier: GPL-3.0-only
 * Distributed WITHOUT ANY WARRANTY; see ../LICENSE.
 * No outgoing requests, persistent storage or response-content logging.
 */

/* global $request, $response, $done */
(function () {
  "use strict";

  const endpoint =
    /^https?:\/\/xunapi\.xunkids\.com\/xunkids\/adservice\/resource\/v2\/pulls\/data(?:\?|$)/;

  function isObject(value) {
    return value !== null && typeof value === "object" && !Array.isArray(value);
  }

  try {
    if (
      typeof $request === "undefined" ||
      typeof $response === "undefined" ||
      !endpoint.test($request.url || "") ||
      typeof $response.body !== "string"
    ) {
      $done({});
      return;
    }

    const result = JSON.parse($response.body);
    if (!isObject(result)) {
      $done({});
      return;
    }

    let changed = false;

    // Clear only existing, nonempty array/object values. Unknown scalar
    // representations, status codes, authentication and other fields pass through.
    function clear(container, keys) {
      if (!isObject(container)) return;
      for (const key of keys) {
        if (!Object.prototype.hasOwnProperty.call(container, key)) continue;
        const value = container[key];
        if (Array.isArray(value) && value.length > 0) {
          container[key] = [];
          changed = true;
        } else if (isObject(value) && Object.keys(value).length > 0) {
          container[key] = {};
          changed = true;
        }
      }
    }

    clear(result.PL, [
      "my_banner",
      "location_icon",
      "adList",
      "startupAds",
      "shakeAds",
      "splash",
      "ads",
    ]);
    clear(result.data, ["adList", "startupAds", "shakeAds", "splash", "ads"]);

    $done(changed ? { body: JSON.stringify(result) } : {});
  } catch (_) {
    // Malformed or unexpected responses remain untouched.
    $done({});
  }
})();
