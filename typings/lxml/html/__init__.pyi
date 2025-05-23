"""
This type stub file was generated by pyright.
"""

from collections.abc import MutableMapping, MutableSet

from .. import etree
from . import defs
from ._setmixin import SetMixin

"""The ``lxml.html`` tool set for HTML handling.
"""
__all__ = [
    "document_fromstring",
    "fragment_fromstring",
    "fragments_fromstring",
    "fromstring",
    "tostring",
    "Element",
    "defs",
    "open_in_browser",
    "submit_form",
    "find_rel_links",
    "find_class",
    "make_links_absolute",
    "resolve_base_href",
    "iterlinks",
    "rewrite_links",
    "parse",
]
XHTML_NAMESPACE = ...
_rel_links_xpath = ...
_options_xpath = ...
_forms_xpath = ...
_class_xpath = ...
_id_xpath = ...
_collect_string_content = ...
_iter_css_urls = ...
_iter_css_imports = ...
_label_xpath = ...
_archive_re = ...
_parse_meta_refresh_url = ...

class Classes(MutableSet):
    """Provides access to an element's class attribute as a set-like collection.
    Usage::

        >>> el = fromstring('<p class="hidden large">Text</p>')
        >>> classes = el.classes  # or: classes = Classes(el.attrib)
        >>> classes |= ['block', 'paragraph']
        >>> el.get('class')
        'hidden large block paragraph'
        >>> classes.toggle('hidden')
        False
        >>> el.get('class')
        'large block paragraph'
        >>> classes -= ('some', 'classes', 'block')
        >>> el.get('class')
        'large paragraph'
    """
    def __init__(self, attributes) -> None: ...
    def add(self, value):  # -> None:
        """
        Add a class.

        This has no effect if the class is already present.
        """

    def discard(self, value):  # -> None:
        """
        Remove a class if it is currently present.

        If the class is not present, do nothing.
        """

    def remove(self, value):  # -> None:
        """
        Remove a class; it must currently be present.

        If the class is not present, raise a KeyError.
        """

    def __contains__(self, name):  # -> bool:
        ...
    def __iter__(self): ...
    def __len__(self):  # -> int:
        ...
    def update(self, values):  # -> None:
        """
        Add all names from 'values'.
        """

    def toggle(self, value):  # -> bool:
        """
        Add a class name if it isn't there yet, or remove it if it exists.

        Returns true if the class was added (and is now enabled) and
        false if it was removed (and is now disabled).
        """

class HtmlMixin:
    def set(self, key, value=...):  # -> None:
        """set(self, key, value=None)

        Sets an element attribute.  If no value is provided, or if the value is None,
        creates a 'boolean' attribute without value, e.g. "<form novalidate></form>"
        for ``form.set('novalidate')``.
        """

    @property
    def classes(self):  # -> Classes:
        """
        A set-like wrapper around the 'class' attribute.
        """

    @classes.setter
    def classes(self, classes):  # -> None:
        ...
    @property
    def base_url(self):
        """
        Returns the base URL, given when the page was parsed.

        Use with ``urlparse.urljoin(el.base_url, href)`` to get
        absolute URLs.
        """

    @property
    def forms(self):  # -> Any:
        """
        Return a list of all the forms
        """

    @property
    def body(self):
        """
        Return the <body> element.  Can be called from a child element
        to get the document's head.
        """

    @property
    def head(self):
        """
        Returns the <head> element.  Can be called from a child
        element to get the document's head.
        """

    @property
    def label(self):  # -> Any | None:
        """
        Get or set any <label> element associated with this element.
        """

    @label.setter
    def label(self, label):  # -> None:
        ...
    @label.deleter
    def label(self):  # -> None:
        ...
    def drop_tree(self):  # -> None:
        """
        Removes this element from the tree, including its children and
        text.  The tail text is joined to the previous element or
        parent.
        """

    def drop_tag(self):  # -> None:
        """
        Remove the tag, but not its children or text.  The children and text
        are merged into the parent.

        Example::

            >>> h = fragment_fromstring('<div>Hello <b>World!</b></div>')
            >>> h.find('.//b').drop_tag()
            >>> print(tostring(h, encoding='unicode'))
            <div>Hello World!</div>
        """

    def find_rel_links(self, rel):  # -> list[Any]:
        """
        Find any links like ``<a rel="{rel}">...</a>``; returns a list of elements.
        """

    def find_class(self, class_name):  # -> Any:
        """
        Find any elements with the given class name.
        """

    def get_element_by_id(self, id, *default):  # -> Any:
        """
        Get the first element in a document with the given id.  If none is
        found, return the default argument if provided or raise KeyError
        otherwise.

        Note that there can be more than one element with the same id,
        and this isn't uncommon in HTML documents found in the wild.
        Browsers return only the first match, and this function does
        the same.
        """

    def text_content(self):  # -> Any:
        """
        Return the text content of the tag (and the text in any children).
        """

    def cssselect(self, expr, translator=...):  # -> Any:
        """
        Run the CSS expression on this element and its children,
        returning a list of the results.

        Equivalent to lxml.cssselect.CSSSelect(expr, translator='html')(self)
        -- note that pre-compiling the expression can provide a substantial
        speedup.
        """

    def make_links_absolute(
        self, base_url=..., resolve_base_href=..., handle_failures=...
    ):  # -> None:
        """
        Make all links in the document absolute, given the
        ``base_url`` for the document (the full URL where the document
        came from), or if no ``base_url`` is given, then the ``.base_url``
        of the document.

        If ``resolve_base_href`` is true, then any ``<base href>``
        tags in the document are used *and* removed from the document.
        If it is false then any such tag is ignored.

        If ``handle_failures`` is None (default), a failure to process
        a URL will abort the processing.  If set to 'ignore', errors
        are ignored.  If set to 'discard', failing URLs will be removed.
        """

    def resolve_base_href(self, handle_failures=...):  # -> None:
        """
        Find any ``<base href>`` tag in the document, and apply its
        values to all links found in the document.  Also remove the
        tag once it has been applied.

        If ``handle_failures`` is None (default), a failure to process
        a URL will abort the processing.  If set to 'ignore', errors
        are ignored.  If set to 'discard', failing URLs will be removed.
        """

    def iterlinks(
        self,
    ):  # -> Generator[tuple[Any, Literal['codebase'], Any, Literal[0]] | tuple[Any, Literal['classid', 'data'], Any, Literal[0]] | tuple[Any, Literal['archive'], str, int] | tuple[Any, str, Any, Literal[0]] | tuple[Any, Literal['content'], str | Any, int | Any] | tuple[Any, Literal['value'], Any, Literal[0]] | tuple[Any, None, str | Any | int, str | Any | int] | tuple[Any, Literal['style'], str | Any, int], Any, None]:
        """
        Yield (element, attribute, link, pos), where attribute may be None
        (indicating the link is in the text).  ``pos`` is the position
        where the link occurs; often 0, but sometimes something else in
        the case of links in stylesheets or style tags.

        Note: <base href> is *not* taken into account in any way.  The
        link you get is exactly the link in the document.

        Note: multiple links inside of a single text string or
        attribute value are returned in reversed order.  This makes it
        possible to replace or delete them from the text string value
        based on their reported text positions.  Otherwise, a
        modification at one text position can change the positions of
        links reported later on.
        """

    def rewrite_links(self, link_repl_func, resolve_base_href=..., base_href=...):  # -> None:
        """
        Rewrite all the links in the document.  For each link
        ``link_repl_func(link)`` will be called, and the return value
        will replace the old link.

        Note that links may not be absolute (unless you first called
        ``make_links_absolute()``), and may be internal (e.g.,
        ``'#anchor'``).  They can also be values like
        ``'mailto:email'`` or ``'javascript:expr'``.

        If you give ``base_href`` then all links passed to
        ``link_repl_func()`` will take that into account.

        If the ``link_repl_func`` returns None, the attribute or
        tag text will be removed completely.
        """

class _MethodFunc:
    """
    An object that represents a method on an element as a function;
    the function takes either an element or an HTML string.  It
    returns whatever the function normally returns, or if the function
    works in-place (and so returns None) it returns a serialized form
    of the resulting document.
    """
    def __init__(self, name, copy=..., source_class=...) -> None: ...
    def __call__(self, doc, *args, **kw):  # -> str | bytes | Any:
        ...

find_rel_links = ...
find_class = ...
make_links_absolute = ...
resolve_base_href = ...
iterlinks = ...
rewrite_links = ...

class HtmlComment(HtmlMixin, etree.CommentBase): ...
class HtmlElement(HtmlMixin, etree.ElementBase): ...
class HtmlProcessingInstruction(HtmlMixin, etree.PIBase): ...
class HtmlEntity(HtmlMixin, etree.EntityBase): ...

class HtmlElementClassLookup(etree.CustomElementClassLookup):
    """A lookup scheme for HTML Element classes.

    To create a lookup instance with different Element classes, pass a tag
    name mapping of Element classes in the ``classes`` keyword argument and/or
    a tag name mapping of Mixin classes in the ``mixins`` keyword argument.
    The special key '*' denotes a Mixin class that should be mixed into all
    Element classes.
    """

    _default_element_classes = ...
    def __init__(self, classes=..., mixins=...) -> None: ...
    def lookup(
        self, node_type, document, namespace, name
    ):  # -> type[HtmlComment] | type[HtmlProcessingInstruction] | type[HtmlEntity] | None:
        ...

_looks_like_full_html_unicode = ...
_looks_like_full_html_bytes = ...

def document_fromstring(html, parser=..., ensure_head_body=..., **kw):  # -> Any:
    ...
def fragments_fromstring(
    html, no_leading_text=..., base_url=..., parser=..., **kw
):  # -> list[Any]:
    """Parses several HTML elements, returning a list of elements.

    The first item in the list may be a string.
    If no_leading_text is true, then it will be an error if there is
    leading text, and it will always be a list of only elements.

    base_url will set the document's base_url attribute
    (and the tree's docinfo.URL).
    """

def fragment_fromstring(html, create_parent=..., base_url=..., parser=..., **kw):
    """
    Parses a single HTML element; it is an error if there is more than
    one element, or if anything but whitespace precedes or follows the
    element.

    If ``create_parent`` is true (or is a tag name) then a parent node
    will be created to encapsulate the HTML in a single element.  In this
    case, leading or trailing text is also allowed, as are multiple elements
    as result of the parsing.

    Passing a ``base_url`` will set the document's ``base_url`` attribute
    (and the tree's docinfo.URL).
    """

def fromstring(html, base_url=..., parser=..., **kw):  # -> Any:
    """
    Parse the html, returning a single element/document.

    This tries to minimally parse the chunk of text, without knowing if it
    is a fragment or a document.

    base_url will set the document's base_url attribute (and the tree's docinfo.URL)
    """

def parse(filename_or_url, parser=..., base_url=..., **kw):
    """
    Parse a filename, URL, or file-like object into an HTML document
    tree.  Note: this returns a tree, not an element.  Use
    ``parse(...).getroot()`` to get the document root.

    You can override the base URL with the ``base_url`` keyword.  This
    is most useful when parsing from a file-like object.
    """

class FormElement(HtmlElement):
    """
    Represents a <form> element.
    """
    @property
    def inputs(self):  # -> InputGetter:
        """
        Returns an accessor for all the input elements in the form.

        See `InputGetter` for more information about the object.
        """

    @property
    def fields(self):  # -> FieldsDict:
        """
        Dictionary-like object that represents all the fields in this
        form.  You can set values in this dictionary to effect the
        form.
        """

    @fields.setter
    def fields(self, value):  # -> None:
        ...
    def form_values(self):  # -> list[Any]:
        """
        Return a list of tuples of the field values for the form.
        This is suitable to be passed to ``urllib.urlencode()``.
        """

    @property
    def action(self):
        """
        Get/set the form's ``action`` attribute.
        """

    @action.setter
    def action(self, value):  # -> None:
        ...
    @action.deleter
    def action(self):  # -> None:
        ...
    @property
    def method(self):  # -> Any:
        """
        Get/set the form's method.  Always returns a capitalized
        string, and defaults to ``'GET'``
        """

    @method.setter
    def method(self, value):  # -> None:
        ...

def submit_form(form, extra_values=..., open_http=...):  # -> _UrlopenRet:
    """
    Helper function to submit a form.  Returns a file-like object, as from
    ``urllib.urlopen()``.  This object also has a ``.geturl()`` function,
    which shows the URL if there were any redirects.

    You can use this like::

        form = doc.forms[0]
        form.inputs["foo"].value = "bar"  # etc
        response = form.submit()
        doc = parse(response)
        doc.make_links_absolute(response.geturl())

    To change the HTTP requester, pass a function as ``open_http`` keyword
    argument that opens the URL for you.  The function must have the following
    signature::

        open_http(method, URL, values)

    The action is one of 'GET' or 'POST', the URL is the target URL as a
    string, and the values are a sequence of ``(name, value)`` tuples with the
    form data.
    """

def open_http_urllib(method, url, values):  # -> _UrlopenRet:
    ...

class FieldsDict(MutableMapping):
    def __init__(self, inputs) -> None: ...
    def __getitem__(self, item): ...
    def __setitem__(self, item, value):  # -> None:
        ...
    def __delitem__(self, item): ...
    def keys(self): ...
    def __contains__(self, item):  # -> bool:
        ...
    def __iter__(self): ...
    def __len__(self):  # -> int:
        ...
    def __repr__(self):  # -> str:
        ...

class InputGetter:
    """
    An accessor that represents all the input fields in a form.

    You can get fields by name from this, with
    ``form.inputs['field_name']``.  If there are a set of checkboxes
    with the same name, they are returned as a list (a `CheckboxGroup`
    which also allows value setting).  Radio inputs are handled
    similarly.  Use ``.keys()`` and ``.items()`` to process all fields
    in this way.

    You can also iterate over this to get all input elements.  This
    won't return the same thing as if you get all the names, as
    checkboxes and radio elements are returned individually.
    """
    def __init__(self, form) -> None: ...
    def __repr__(self):  # -> str:
        ...
    def __getitem__(self, name):  # -> RadioGroup | CheckboxGroup:
        ...
    def __contains__(self, name):  # -> bool:
        ...
    def keys(self):  # -> list[Any]:
        """
        Returns all unique field names, in document order.

        :return: A list of all unique field names.
        """

    def items(self):  # -> list[Any]:
        """
        Returns all fields with their names, similar to dict.items().

        :return: A list of (name, field) tuples.
        """

    def __iter__(self): ...
    def __len__(self):  # -> int:
        ...

class InputMixin:
    """
    Mix-in for all input elements (input, select, and textarea)
    """
    @property
    def name(self):
        """
        Get/set the name of the element
        """

    @name.setter
    def name(self, value):  # -> None:
        ...
    @name.deleter
    def name(self):  # -> None:
        ...
    def __repr__(self):  # -> str:
        ...

class TextareaElement(InputMixin, HtmlElement):
    """
    ``<textarea>`` element.  You can get the name with ``.name`` and
    get/set the value with ``.value``
    """
    @property
    def value(self):  # -> Any | Literal['']:
        """
        Get/set the value (which is the contents of this element)
        """

    @value.setter
    def value(self, value):  # -> None:
        ...
    @value.deleter
    def value(self):  # -> None:
        ...

class SelectElement(InputMixin, HtmlElement):
    """
    ``<select>`` element.  You can get the name with ``.name``.

    ``.value`` will be the value of the selected option, unless this
    is a multi-select element (``<select multiple>``), in which case
    it will be a set-like object.  In either case ``.value_options``
    gives the possible values.

    The boolean attribute ``.multiple`` shows if this is a
    multi-select.
    """
    @property
    def value(self):  # -> MultipleSelectOptions | LiteralString | Any | None:
        """
        Get/set the value of this select (the selected option).

        If this is a multi-select, this is a set-like object that
        represents all the selected options.
        """

    @value.setter
    def value(self, value):  # -> None:
        ...
    @value.deleter
    def value(self):  # -> None:
        ...
    @property
    def value_options(self):  # -> list[Any]:
        """
        All the possible values this select can have (the ``value``
        attribute of all the ``<option>`` elements.
        """

    @property
    def multiple(self):  # -> bool:
        """
        Boolean attribute: is there a ``multiple`` attribute on this element.
        """

    @multiple.setter
    def multiple(self, value):  # -> None:
        ...

class MultipleSelectOptions(SetMixin):
    """
    Represents all the selected options in a ``<select multiple>`` element.

    You can add to this set-like option to select an option, or remove
    to unselect the option.
    """
    def __init__(self, select) -> None: ...
    @property
    def options(self):  # -> Any:
        """
        Iterator of all the ``<option>`` elements.
        """

    def __iter__(self):  # -> Generator[LiteralString | Any, Any, None]:
        ...
    def add(self, item):  # -> None:
        ...
    def remove(self, item):  # -> None:
        ...
    def __repr__(self):  # -> str:
        ...

class RadioGroup(list):
    """
    This object represents several ``<input type=radio>`` elements
    that have the same name.

    You can use this like a list, but also use the property
    ``.value`` to check/uncheck inputs.  Also you can use
    ``.value_options`` to get the possible values.
    """
    @property
    def value(self):  # -> None:
        """
        Get/set the value, which checks the radio with that value (and
        unchecks any other value).
        """

    @value.setter
    def value(self, value):  # -> None:
        ...
    @value.deleter
    def value(self):  # -> None:
        ...
    @property
    def value_options(self):  # -> list[Any]:
        """
        Returns a list of all the possible values.
        """

    def __repr__(self):  # -> str:
        ...

class CheckboxGroup(list):
    """
    Represents a group of checkboxes (``<input type=checkbox>``) that
    have the same name.

    In addition to using this like a list, the ``.value`` attribute
    returns a set-like object that you can add to or remove from to
    check and uncheck checkboxes.  You can also use ``.value_options``
    to get the possible values.
    """
    @property
    def value(self):  # -> CheckboxValues:
        """
        Return a set-like object that can be modified to check or
        uncheck individual checkboxes according to their value.
        """

    @value.setter
    def value(self, value):  # -> None:
        ...
    @value.deleter
    def value(self):  # -> None:
        ...
    @property
    def value_options(self):  # -> list[Any]:
        """
        Returns a list of all the possible values.
        """

    def __repr__(self):  # -> str:
        ...

class CheckboxValues(SetMixin):
    """
    Represents the values of the checked checkboxes in a group of
    checkboxes with the same name.
    """
    def __init__(self, group) -> None: ...
    def __iter__(self):  # -> Iterator[Any]:
        ...
    def add(self, value):  # -> None:
        ...
    def remove(self, value):  # -> None:
        ...
    def __repr__(self):  # -> str:
        ...

class InputElement(InputMixin, HtmlElement):
    """
    Represents an ``<input>`` element.

    You can get the type with ``.type`` (which is lower-cased and
    defaults to ``'text'``).

    Also you can get and set the value with ``.value``

    Checkboxes and radios have the attribute ``input.checkable ==
    True`` (for all others it is false) and a boolean attribute
    ``.checked``.

    """
    @property
    def value(self):  # -> Literal['on'] | None:
        """
        Get/set the value of this element, using the ``value`` attribute.

        Also, if this is a checkbox and it has no value, this defaults
        to ``'on'``.  If it is a checkbox or radio that is not
        checked, this returns None.
        """

    @value.setter
    def value(self, value):  # -> None:
        ...
    @value.deleter
    def value(self):  # -> None:
        ...
    @property
    def type(self):  # -> Any:
        """
        Return the type of this element (using the type attribute).
        """

    @type.setter
    def type(self, value):  # -> None:
        ...
    @property
    def checkable(self):  # -> bool:
        """
        Boolean: can this element be checked?
        """

    @property
    def checked(self):  # -> bool:
        """
        Boolean attribute to get/set the presence of the ``checked``
        attribute.

        You can only use this on checkable input types.
        """

    @checked.setter
    def checked(self, value):  # -> None:
        ...

class LabelElement(HtmlElement):
    """
    Represents a ``<label>`` element.

    Label elements are linked to other elements with their ``for``
    attribute.  You can access this element with ``label.for_element``.
    """
    @property
    def for_element(self):  # -> None:
        """
        Get/set the element this label points to.  Return None if it
        can't be found.
        """

    @for_element.setter
    def for_element(self, other):  # -> None:
        ...
    @for_element.deleter
    def for_element(self):  # -> None:
        ...

def html_to_xhtml(html):  # -> None:
    """Convert all tags in an HTML tree to XHTML by moving them to the
    XHTML namespace.
    """

def xhtml_to_html(xhtml):  # -> None:
    """Convert all tags in an XHTML tree to HTML by removing their
    XHTML namespace.
    """

__str_replace_meta_content_type = ...
__bytes_replace_meta_content_type = ...

def tostring(
    doc,
    pretty_print=...,
    include_meta_content_type=...,
    encoding=...,
    method=...,
    with_tail=...,
    doctype=...,
):  # -> str | bytes:
    """Return an HTML string representation of the document.

    Note: if include_meta_content_type is true this will create a
    ``<meta http-equiv="Content-Type" ...>`` tag in the head;
    regardless of the value of include_meta_content_type any existing
    ``<meta http-equiv="Content-Type" ...>`` tag will be removed

    The ``encoding`` argument controls the output encoding (defaults to
    ASCII, with &#...; character references for any characters outside
    of ASCII).  Note that you can pass the name ``'unicode'`` as
    ``encoding`` argument to serialise to a Unicode string.

    The ``method`` argument defines the output method.  It defaults to
    'html', but can also be 'xml' for xhtml output, or 'text' to
    serialise to plain text without markup.

    To leave out the tail text of the top-level element that is being
    serialised, pass ``with_tail=False``.

    The ``doctype`` option allows passing in a plain string that will
    be serialised before the XML tree.  Note that passing in non
    well-formed content here will make the XML output non well-formed.
    Also, an existing doctype in the document tree will not be removed
    when serialising an ElementTree instance.

    Example::

        >>> from lxml import html
        >>> root = html.fragment_fromstring('<p>Hello<br>world!</p>')

        >>> html.tostring(root)
        b'<p>Hello<br>world!</p>'
        >>> html.tostring(root, method='html')
        b'<p>Hello<br>world!</p>'

        >>> html.tostring(root, method='xml')
        b'<p>Hello<br/>world!</p>'

        >>> html.tostring(root, method='text')
        b'Helloworld!'

        >>> html.tostring(root, method='text', encoding='unicode')
        u'Helloworld!'

        >>> root = html.fragment_fromstring('<div><p>Hello<br>world!</p>TAIL</div>')
        >>> html.tostring(root[0], method='text', encoding='unicode')
        u'Helloworld!TAIL'

        >>> html.tostring(root[0], method='text', encoding='unicode', with_tail=False)
        u'Helloworld!'

        >>> doc = html.document_fromstring('<p>Hello<br>world!</p>')
        >>> html.tostring(doc, method='html', encoding='unicode')
        u'<html><body><p>Hello<br>world!</p></body></html>'

        >>> print(html.tostring(doc, method='html', encoding='unicode',
        ...          doctype='<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN"'
        ...                  ' "http://www.w3.org/TR/html4/strict.dtd">'))
        <!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">
        <html><body><p>Hello<br>world!</p></body></html>
    """

def open_in_browser(doc, encoding=...):  # -> None:
    """
    Open the HTML document in a web browser, saving it to a temporary
    file to open it.  Note that this does not delete the file after
    use.  This is mainly meant for debugging.
    """

class HTMLParser(etree.HTMLParser):
    """An HTML parser that is configured to return lxml.html Element
    objects.
    """
    def __init__(self, **kwargs) -> None: ...

class XHTMLParser(etree.XMLParser):
    """An XML parser that is configured to return lxml.html Element
    objects.

    Note that this parser is not really XHTML aware unless you let it
    load a DTD that declares the HTML entities.  To do this, make sure
    you have the XHTML DTDs installed in your catalogs, and create the
    parser like this::

        >>> parser = XHTMLParser(load_dtd=True)

    If you additionally want to validate the document, use this::

        >>> parser = XHTMLParser(dtd_validation=True)

    For catalog support, see http://www.xmlsoft.org/catalog.html.
    """
    def __init__(self, **kwargs) -> None: ...

def Element(*args, **kw):
    """Create a new HTML Element.

    This can also be used for XHTML documents.
    """

html_parser = ...
xhtml_parser = ...
