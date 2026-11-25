# Python web-request entry packs

These five packs publish the request-read surface of Flask,
Werkzeug and Django for bifrost-dev#14549. They are the public half of a split
the owner chose on 2026-11-19: the request entry points are public, and the
deep framework models (response sinks, sanitizers, versioned internals) stay in
`bifrost-premium-packs`. The member list below is the one the owner reviewed
and approved.

| Pack | Version | Activates on | Kind |
| --- | --- | --- | --- |
| `bifrost.python-flask-request-declarations` | 0.1.0 | `pkg:pypi/flask` `>=3.1.0, <3.2.0` | declarations |
| `bifrost.python-werkzeug-request-declarations` | 0.1.0 | `pkg:pypi/werkzeug` `>=3.1.0, <3.2.0` | declarations |
| `bifrost.python-werkzeug-request-summaries` | 0.1.0 | `pkg:pypi/werkzeug` `>=3.1.0, <3.2.0` | procedure summaries |
| `bifrost.python-django-request-declarations` | 0.1.0 | `pkg:pypi/django` `>=5.2.0, <5.3.0` | declarations |
| `bifrost.python-django-request-summaries` | 0.1.0 | `pkg:pypi/django` `>=5.2.0, <5.3.0` | procedure summaries |

## Activation

Third-party Python packs need `pkg:pypi/<name>` activation evidence. From
Bifrost 0.15.4 on, the engine derives it from `uv.lock`, `poetry.lock` or pinned
requirements as well as from a declared Python environment with wheel archives
(bifrost-dev#14581). The owner decided on 2026-11-19 that such evidence may bind
these members `:proof exact`. Earlier engines report `incompatible: no
activation evidence names package pkg:pypi/<name>`.

`native-generation.json` builds all five, so the first packs release cut after
this change delivers them; `packs/v0.16.0` and earlier do not. The Flask and
Django request rules run by default from the next rules release (opt-in in
`rules/v0.17.0`); that release needs an engine carrying bifrost-dev#15470. The
fixtures qualify the packs on 0.15.4.

## Reviewed claims

Each claim was checked against the upstream source at the pinned version:
pallets/werkzeug `3.1.0`, pallets/flask `3.1.0`, and django/django
`stable/5.2.x`. The version ranges stop at the next minor release because
nothing later was reviewed.

Flask and Werkzeug:

- `flask.request` is a `werkzeug.local.LocalProxy` whose member dispatch goes to
  `werkzeug.wrappers.Request` (`flask/globals.py`). Flask's own
  `flask.wrappers.Request` subclass overrides neither `args`, `form`, `cookies`,
  `headers` nor `get_json`. The type names follow the premium Werkzeug model
  that bifrost-dev#12429 verified binds exactly.
- `Request.args`, `Request.form` and `Request.cookies` are exactly
  `werkzeug.datastructures.structures.ImmutableMultiDict`.
  `parameter_storage_class` and `dict_storage_class` both default to that class
  in `sansio/request.py`, and every path of `_load_form_data` builds it. An
  application `Request` subclass that overrides these attributes falls outside
  the claim.
- `Request.headers` is exactly `werkzeug.datastructures.headers.EnvironHeaders`:
  `wrappers/request.py` passes `EnvironHeaders(environ)` to the sans-IO
  constructor, which stores it unchanged.
- `ImmutableMultiDict.get(key, default=None, type=None)` and
  `getlist(key, type=None)` are inherited from `TypeConversionDict` and
  `MultiDict`, and neither immutable mixin overrides them. The same holds for
  `EnvironHeaders.get` and `getlist`, inherited from `Headers`. The members are
  declared on the receiver's own class, because these declarations carry no
  base classes.
- `Request.get_json(force=False, silent=False, cache=True)` is defined on
  `werkzeug.wrappers.Request`. Its result is the parsed request body.

Django:

- `HttpRequest.GET` and `HttpRequest.POST` are exactly `django.http.QueryDict`.
  `HttpRequest.__init__` assigns empty `QueryDict` objects. `WSGIRequest.GET`
  builds a `QueryDict` from `QUERY_STRING`. Every branch of
  `_load_post_and_files`, `_mark_post_parse_error` and `MultiPartParser.parse`
  produces a `QueryDict`. Code that assigns another object to `request.POST`
  falls outside the claim.
- `QueryDict.get(key, default=None)` and `getlist(key, default=None)` are
  inherited unchanged from `MultiValueDict`.

## Summaries

Every summary is complete: a receiver-to-result transfer, a transfer from each
optional default or `type` argument to the result, and a receiver-to-exception
transfer. The exception transfer exists because a `type` callback or JSON
parsing can raise. `covers_overrides` is false. `CombinedMultiDict`, for
example, subclasses `ImmutableMultiDict` and overrides `get`. With simulated
activation on bifrost-dev 709884428bf, the summaries carry request taint
through `get` and `getlist` with this setting.

## How the rules use these packs

The `flask-request-to-urlopen` and `django-request-to-urlopen` rules select the accessor read (`request.args`, `request.GET`) with
`resolved-value`, not the `get` call. So a value is tainted only when it comes
from a request, and a `QueryDict` or `ImmutableMultiDict` the application
built is not a source. A `:receiver-type` qualifier on a call source would not
work here anyway: the policy locator rejects receiver types from a pack whose
completeness is `partial` (`qualified-receiver-locator-partial`).
`Request.get_json` is declared and summarized, but no rule uses it as a source
yet. Called through the `LocalProxy`, it gives `CallBindingDispatchPartial`.

## Excluded on purpose

- `Request.values`: a `CombinedMultiDict`, which overrides `get`.
- `Request.data` and Django `HttpRequest.body`: property reads, which the
  call-shaped source selectors cannot select.
- Django `COOKIES` and `META`: plain `dict` values, so a `dict.get` source
  would select every dictionary in the program.
- Starlette and FastAPI: deferred. No reviewed model exists yet.
- Response sinks, `Flask.run`, `make_response`, sanitizers and other
  distributions: these stay premium.

The packs carry the repository's `Apache-2.0` model license. They describe API
identity and value flow, not library code, and they set
`safety.review_required: false` as first-party content.
