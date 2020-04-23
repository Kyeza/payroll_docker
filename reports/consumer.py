from channels.consumer import AsyncConsumer


class PayrollConsumer(AsyncConsumer):

    async def websocket_connect(self, event):
        print("websocket connected", event)

        await self.send({
            "type": "websocket.accept"
        })

    async def websocket_receive(self, event):
        print("websocket message received", event)

    async def websocket_disconnect(self, event):
        print("websocket disconnect", event)

    async def processing_notification(self, event):
        """
        coroutine for sending notification when the processing job is finished
        :param event:
        :return:
        """
        print("websocket processing_notification", event)
        await self.send({
            'type': 'websocket.send',
            'text': event['text']
        })
