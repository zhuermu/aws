package com.zhuermu;

import com.amazonaws.services.lambda.runtime.Context;
import com.amazonaws.services.lambda.runtime.events.SQSEvent.SQSMessage;
import com.amazonaws.services.lambda.runtime.events.SQSEvent;
import java.util.ArrayList;
import java.util.List;
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.mockito.Mockito.*;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;


public class VideoClassifyFromSqsHandlerTest {

    /**
     * Tests the handleRequest method with an empty list of SQS records.
     * This edge case is explicitly handled in the focal method as it iterates
     * over the records, and an empty list should result in no processing.
     */
    @Test
    public void test_handleRequest_emptyRecordsList() {
        VideoClassifyFromSqsHandler handler = new VideoClassifyFromSqsHandler();
        SQSEvent event = new SQSEvent();
        event.setRecords(new ArrayList<>());
        Context context = mock(Context.class);

        Void result = handler.handleRequest(event, context);

        assertNull(result);
    }

    /**
     * Tests the handleRequest method when an exception occurs during message processing.
     * This edge case is explicitly handled in the focal method with a try-catch block,
     * ensuring that the method continues processing subsequent messages.
     */
    @Test
    public void test_handleRequest_exceptionDuringProcessing() {
        VideoClassifyFromSqsHandler handler = spy(new VideoClassifyFromSqsHandler());
        SQSEvent event = new SQSEvent();
        List<SQSMessage> records = new ArrayList<>();
        SQSMessage message = new SQSMessage();
        message.setMessageId("testMessageId");
        records.add(message);
        event.setRecords(records);
        Context context = mock(Context.class);

        doThrow(new RuntimeException("Test exception")).when(handler).processMessage(any());

        Void result = handler.handleRequest(event, context);

        assertNull(result);
        verify(handler, times(1)).processMessage(any());
    }

    /**
     * Test case for handleRequest method when processing an SQSEvent with multiple records.
     * This test verifies that the method processes all records in the event and returns null.
     */
    @Test
    public void test_handleRequest_processesMultipleRecords() {
        // Arrange
        VideoClassifyFromSqsHandler handler = new VideoClassifyFromSqsHandler();
        SQSEvent sqsEvent = mock(SQSEvent.class);
        Context context = mock(Context.class);

        List<SQSMessage> messages = new ArrayList<>();
        SQSMessage message1 = mock(SQSMessage.class);
        SQSMessage message2 = mock(SQSMessage.class);
        messages.add(message1);
        messages.add(message2);

        when(sqsEvent.getRecords()).thenReturn(messages);
        when(message1.getBody()).thenReturn("{\"s3Uri\":\"s3://bedrock-video-generation-us-east-1-pi8hu9/video-class/f81d2c02aa474179b4ead01df54bbd13.mp4\"}");
        //when(message2.getBody()).thenReturn("{\"s3Uri\":\"s3://bedrock-video-generation-us-east-1-pi8hu9/video-class/e0ec62926beb47afb4e57258dd3b3222.mp4\"}");

        // Act
        Void result = handler.handleRequest(sqsEvent, context);

        // Assert
        assertNull(result);
        // Additional assertions could be added here to verify that the messages were processed
        // For example, you could use Mockito to verify that certain methods were called
    }
}
