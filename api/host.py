#from insights_connexion.db.base import session
from app.models import Host, convert_json_facts_to_dict
from app import db

from sqlalchemy.orm.attributes import flag_modified


def addHost(host):
    print("addHost()")
    print("host:", host)

    # Required inputs:
    # account
    # canonical_facts

    canonical_facts = host.get("canonical_facts")

    found_host = Host.query.filter(
                         Host.canonical_facts.comparator.contains(canonical_facts) |
                         Host.canonical_facts.comparator.contained_by(canonical_facts)
                       ).first()

    if not found_host:
        print("Creating a new host")
        host = Host.from_json(host)
        print("FACTS:", host.facts)
        host.save()
        return {'count': 0, 'results': host.to_json()}, 201
    else:
        print("Updating host...")

        # ---------------------------------------------------------------
        # FIXME: The update logic needs to be moved into the model object
        # ---------------------------------------------------------------

        # FIXME: make sure new canonical facts are added
        found_host.canonical_facts.update(canonical_facts)
        flag_modified(found_host, "canonical_facts")

        display_name = host.get("display_name", None)
        if display_name:
            found_host.display_name = display_name

        facts = host.get("facts", [])
        if facts:
            facts_dict = convert_json_facts_to_dict(facts)
            for input_namespace, input_facts in facts_dict.items():
                if found_host.facts:
                    if input_namespace in found_host.facts:
                        found_host.facts[input_namespace].extend(input_facts)
                    else:
                        found_host.facts[input_namespace] = input_facts
                else:
                    found_host.facts = facts
                flag_modified(found_host, "facts")

        tags = host.get("tags", [])
        if tags:
            found_host.tags.extend(tags)
            flag_modified(found_host, "tags")

        print("*** Updated host:", found_host)

        db.session.commit()
        return {'count': 0, 'results': found_host.to_json()}, 200


def getHostList(tag=None):
    print(f"getHostList(tag={tag})")

    if tag:
        host_list = findHostsByTag(tag)
    else:
        host_list = Host.get_all()

    json_host_list = [host.to_json() for host in host_list]

    # FIXME: pagination
    return json_host_list, 200


def findHostsByTag(tag):
    print(f"findHostsByTag({tag})")
    found_host_list = Host.query.filter(
            Host.tags.comparator.contains(tag)).all()
    print("found_host_list:", found_host_list)
    return found_host_list


def getHostById(hostId):
    print(f"getHostById({hostId})")

    print(type(hostId[0]))

    host_id_list = [int(host_id) for host_id in hostId]

    found_host_list = Host.query.filter(Host.id.in_(host_id_list)).all()

    json_host_list = [host.to_json() for host in found_host_list]

    return {'count': 0, 'results': json_host_list}, 200


def updateHostWithForm():
    print("updateHostWithForm()")


def deleteHost(hostId):
    print(f"deleteHost({hostId})")


def replaceFacts(hostId, namespace):
    print(f"replaceFacts({hostId}, {namespace})")


def mergeFacts(hostId, namespace):
    print(f"mergeFacts({hostId}, {namespace})")
    found_host = Host.query.filter(
            Host.facts.contains([{"namespace": namespace}])).all()

            # works
            #Host.canonical_facts["key5"].astext == "value5" ).all()

    print("found_host:", found_host)


def handleTagOperation(hostId, tag_op):
    print(f"handleTagOperation({hostId},{tag_op})")

    found_host = Host.query.filter(Host.id.in_(hostId)).all()
    print("found_host:", found_host)
