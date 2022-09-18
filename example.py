import asyncio
import pprint
from uuid import UUID

from circle_client import CircleClient

client = CircleClient("KEY HERE")


# How to search for a user using their display name
# You can also search for contact_info values
# Returns a list, you can specify the maximum length with the `n` field
async def search_users():
    users = await client.search_users(
        display_name="Bob"
    )
    pprint.pprint(users)
    users2 = await client.search_users(
        contact_info_key="some_identifying_key",
        contact_info_value="some_identifying_value"
    )
    pprint.pprint(users2)


# You can search shapes by shape_name
# Supports pagination and maximum number of shapes to return
# If you neglect to supply a shape_name, it will just return all shapes
async def search_shapes():
    shapes = await client.search_shapes(
        shape_name="Circle",
        n=10,
        p=0
    )
    pprint.pprint(shapes)


# Fetch a single shape or user using their UUID
async def search_with_uuid():
    user = await client.get_user(UUID("54b46933-96a0-4eb1-85af-b9fd1ad28e8d"))
    shape = await client.get_shape(UUID("ebc2cc32-3791-44b1-9cdd-07b9a3bda468"))
    pprint.pprint(user)
    pprint.pprint(shape)


# Create a user with a display_name and some contact info
# the `group` field denotes whether the user represents a group chat
# Group chats require a "group user" to associate all messages in the group with
async def create_user():
    user = await client.create_user(
        display_name="ALICE IS SO PRETTY",
        group=False,
        contact_info={
            "some_identifying_value": 1200
        }
    )
    pprint.pprint(user)


# Update a single user by searching for a user, making some changes, and using the update function
# You can change the value of any field except `id`
async def update():
    users = await client.search_users(display_name="ALICE IS SO PRETTY")
    user = users[0]
    user.contact_info["some_contact_info_key"] = "some_contact_info_value"
    user = await client.update_user(user)
    pprint.pprint(user)


# Allocates tokens to a user
# Must be done when their account is created, and every time they hit their quota thereafter
async def allocate_tokens():
    user = await client.search_users(display_name="ALICE IS SO PRETTY")[0]
    allocated = await client.allocate_tokens(user.id, 100)
    pprint.pprint(allocated)


# Sends a message between one user and one shape
# If you want to send a message to a group, you need a group user and a user for the sender of the message
# sender_id is the sender's user id, and user_id is the group user's user id
async def send_message():
    users = await client.search_users(display_name="ALICE IS SO PRETTY")
    shapes = await client.search_shapes(shape_name="Some Kind Of New And Shiny Shape")
    user = users[0]
    shape = shapes[0]
    message = await client.send_message(
        user_id=user.id,
        shape_id=shape.id,
        message="This is an example message to be sent from a user to a shape"
    )
    pprint.pprint(message)


# Resets message history between a shape and a user
# Works for group users and single users
async def reset_message_history():
    users = await client.search_users(display_name="ALICE IS SO PRETTY")
    shapes = await client.search_shapes(shape_name="Some Kind Of New And Shiny Shape")
    user = users[0]
    shape = shapes[0]
    wack = await client.wack(shape.id, user.id)
    pprint.pprint(wack)


# Generates a reply
# In a one-on-one conversation, supply the user's ID, in a group, supply the group user's ID
async def generate_reply():
    users = await client.search_users(display_name="ALICE IS SO PRETTY")
    shapes = await client.search_shapes(shape_name="Some Kind Of New And Shiny Shape")
    user = users[0]
    shape = shapes[0]
    reply = await client.generate_reply(shape.id, user.id)
    pprint.pprint(reply)


async def test():
    await search_shapes()
    await search_users()
    await search_with_uuid()
    await create_user()
    await update()
    await allocate_tokens()
    await send_message()
    await reset_message_history()
    await generate_reply()

asyncio.get_event_loop().run_until_complete(test())
