import time
import wasabi

from sqlalchemy.orm.exc import NoResultFound
from .models import Page, Revision, new_session


_log = wasabi.Printer()


def get_all_pages():
    with new_session() as session:

        pages = session.query(Page).all()
        num_revs = session.query(Revision).count()

        check = 0
        for page in pages:
            page.revcount = len(page.revisions)
            check += page.revcount
        abandoned = num_revs - check

        ctx = {
            'v_pages': pages,
            'v_num_pages': len(pages),
            'v_num_revs': num_revs,
            'v_num_abandoned': abandoned,
        }

        return ctx


def get_page_by_id(id: int):
    pass


def get_page_by_title(title: str):
    with new_session() as session:
        title = Page.format_title(title)
        try:
            page = session.query(Page).filter_by(title=title).one()
        except NoResultFound:
            return 'No match found'
        # TODO Handle this!

        rev = page.revisions[-1]  # latest revision

        ctx = {
            'v_page_id': page.id,
            'v_pretty_title': Page.pretty_title(page.title),
            'v_content': rev.content
        }

        return ctx


def del_page_by_id(id: int):
    with new_session() as session:
        try:
            page = session.query(Page).filter_by(id=id).one()
            session.delete(page)  # delete page and its revs
            msg = f'Page(id: {id}) deleted successfully'
        except NoResultFound:
            msg = f'Delete Failed- Page(id: {id}) doesnt exist!'
        finally:
            session.commit()

        ctx = {
            'v_title': f'Delete Page {id}',
            'v_message': msg
        }

        return ctx


def create_new_page(title: str, note: str, rev_content) -> Page:
    with new_session() as session:
        # page
        page = Page()
        page.title = Page.format_title(title)
        page.note = note

        # Revision
        rev = Revision()
        rev.content = rev_content
        rev.timestamp = int(time.time())

        if page.revisions:
            # WTF IS THIS ???
            _log.fail('create_new_page: Page already exists!: ', page)
            raise Exception('Page already exists!')

        page.revisions.append(rev)
        session.add(page)
        session.commit()
        return page


def gen_dummy_pages():
    """ Generate dummy pages for testing """

    with open('static/dummy_data.txt', 'r') as f:
        data = f.read()

    pages = data.split('======')
    assert len(pages) == 3

    p1 = Page(title=Page.format_title('wiki'))
    p1.revisions.append(Revision(content=pages[0], timestamp=int(time.time())))

    p2 = Page(title=Page.format_title('Website'))
    p2.revisions.append(Revision(content=pages[1], timestamp=int(time.time())))

    p3 = Page(title=Page.format_title('stock market'))
    p3.revisions.append(Revision(content=pages[2], timestamp=int(time.time())))

    with new_session() as session:
        session.add_all([p1, p2, p3])
        session.commit()

    _log.good('Pages generated successfully')
